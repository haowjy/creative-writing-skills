/*
 * The journeys view: journeys/index.md lists the journeys, each journey page is a row of
 * step cards (title, a place for the step's screenshot when it has one, Does, Sees). A card
 * opens its links in the panel: map links go to the map at that box, machine links open in the
 * doc view; a link to a flow page opens the flow. Under the journeys, "What happens underneath"
 * lists the flows (the list items of flows/index.md). The route is `#journeys[/<journey>[/<step number>]]`.
 */
import { MAP_DIR, NAV } from "./config.js";
import { paintInline, route } from "./markdown.js";
import { item, JOURNEY_KEYS, linksOf } from "./pages.js";
import { shotCrop } from "./screens.js";
import { adjustablePanel, el, fetchPage, fetchRepoFile, showPanel } from "./shell.js";

const JOURNEYS = `${MAP_DIR}/journeys`;
const FLOWS_INDEX = `${MAP_DIR}/flows/index.md`;

/** Mounts the journeys into `host`; `nav.replace(hash)` changes the address without a history entry. Returns { select(id, step), dispose() }. */
export async function createJourneys(host, { nav, screens }) {
  const content = el("div", { class: "journeys" });
  const panel = el("aside", { class: "panel", "aria-label": "Selected step" });
  host.replaceChildren(content, panel);
  const disposePanel = adjustablePanel(host, panel);
  // A project may have no flows; the check holds the flows page to what exists.
  const flowLines = (await fetchRepoFile(FLOWS_INDEX).catch(() => ""))
    .split("\n")
    .filter((l) => l.startsWith("- "));
  const hrefs = [
    ...new Set(linksOf(await fetchRepoFile(`${JOURNEYS}/index.md`)).map((l) => l.href)),
  ];
  const journeys = await Promise.all(
    hrefs
      .filter((h) => /^[\w-]+\.md$/.test(h) && h !== "index.md")
      .map(async (href) => ({
        id: href.slice(0, -3),
        path: `${JOURNEYS}/${href}`,
        page: await fetchPage(`${JOURNEYS}/${href}`),
      })),
  );
  content.replaceChildren(
    ...journeys.map((j) =>
      el(
        "section",
        { class: "journey", id: j.id },
        el("h2", null, j.page.title),
        paragraph(j.page.intro, j.path),
        el(
          "div",
          { class: "steps" },
          j.page.sections.map((s, i) => card(j, s, i)),
        ),
      ),
    ),
  );
  if (flowLines.length)
    content.append(
      el(
        "section",
        { class: "journey underneath" },
        el("h2", null, "What happens underneath"),
        el(
          "ul",
          null,
          flowLines.map((l) => {
            const li = el("li");
            paintInline(li, l.slice(2), FLOWS_INDEX);
            return li;
          }),
        ),
      ),
    );
  enablePan();

  function paragraph(markdown, path) {
    const p = el("p", { class: "sub" });
    paintInline(p, markdown, path);
    return p;
  }

  /** The text after "Does:" / "Sees:" in a step's paragraphs. */
  function field(section, name) {
    return (
      section.paragraphs
        .find((p) => p.startsWith(`${name}:`))
        ?.slice(name.length + 1)
        .trim() ?? ""
    );
  }

  function card(journey, section, i) {
    const open = () => {
      nav.replace(`#journeys/${journey.id}/${i + 1}`);
      showPanel();
      select(journey.id, i + 1);
    };
    return el(
      "article",
      {
        class: "step",
        "data-step": `${journey.id}/${i + 1}`,
      },
      el("div", { class: "step-no" }, `${i + 1}`),
      el("h3", null, el("button", { type: "button", class: "step-title", onclick: open }, section.id)),
      item(section, "Shot") && shotCrop(screens, item(section, "Shot").value, 400),
      el("h4", null, "Does"),
      paragraph(field(section, "Does"), journey.path),
      el("h4", null, "Sees"),
      paragraph(field(section, "Sees"), journey.path),
    );
  }

  function select(id, n) {
    for (const c of content.querySelectorAll(".step"))
      c.classList.toggle("is-selected", c.dataset.step === `${id}/${n}`);
    const journey = journeys.find((j) => j.id === id);
    const section = journey?.page.sections[Number(n) - 1];
    if (!section) {
      panel.replaceChildren(
        el(
          "div",
          { class: "panel-body" },
          el("h2", null, NAV.journeys),
          el("p", { class: "panel-hint" }, "Click a step to see where it lives in the system."),
        ),
      );
      if (journey) content.querySelector(`#${CSS.escape(id)}`)?.scrollIntoView();
      return;
    }
    content
      .querySelector(`[data-step="${id}/${n}"]`)
      ?.scrollIntoView({ inline: "nearest", block: "nearest" });
    const groups = JOURNEY_KEYS.flatMap((key) => {
      const links = linksOf(item(section, key)?.value ?? "");
      if (key === "Shot") return [];
      const isFlow = (l) => l.href.includes("flows/");
      const lists =
        key === "Map"
          ? [
              ["On the map", links.filter((l) => !isFlow(l))],
              ["What happens underneath", links.filter(isFlow)],
            ]
          : [["State machines", links]];
      return lists
        .filter(([, ls]) => ls.length)
        .map(([title, ls]) =>
          el(
            "section",
            null,
            el("h3", null, title),
            el(
              "ul",
              null,
              ls.map((l) =>
                el(
                  "li",
                  null,
                  el("a", { href: route(journey.path, l.href)?.href ?? l.href }, l.label),
                ),
              ),
            ),
          ),
        );
    });
    panel.replaceChildren(
      el(
        "div",
        { class: "panel-body" },
        el("h2", null, section.id),
        el("p", { class: "sub" }, journey.page.title),
        ...groups,
      ),
    );
  }

  /** Drag the card rows sideways. */
  function enablePan() {
    let drag = null;
    content.addEventListener("pointerdown", (event) => {
      const row = event.target.closest(".steps");
      if (!row || event.button) return;
      drag = { row, x: event.clientX, left: row.scrollLeft, moved: false };
    });
    content.addEventListener("pointermove", (event) => {
      if (!drag) return;
      const dx = event.clientX - drag.x;
      if (!drag.moved && Math.abs(dx) < 4) return;
      drag.moved = true;
      drag.row.scrollLeft = drag.left - dx;
    });
    const end = () => {
      if (drag?.moved)
        content.addEventListener("click", (e) => e.stopPropagation(), {
          capture: true,
          once: true,
        });
      drag = null;
    };
    content.addEventListener("pointerup", end);
    content.addEventListener("pointercancel", end);
  }

  return { select, dispose: disposePanel };
}
