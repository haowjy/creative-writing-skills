/*
 * Screenshots on the map: the config's `screens` manifest (shot -> image, size, title, regions
 * with bounds, a label, a code path and the box each region is explained by). A box's panel
 * shows the crop of the region its `Shot` names and the whole screen with every region outlined,
 * numbered and linked to its box; Read view and a journey step show the crop. A crop is a CSS
 * background of the full image, so there is one image per screen and none per box.
 */
import { SCREENS } from "./config.js";
import { pathLink } from "./markdown.js";
import { resolveHref, resolveShot } from "./pages.js";
import { el, fetchRepoFile, repoUrl } from "./shell.js";

/**
 * The manifest, null when the project has none, or the Error when it didn't load or parse: logged
 * here, and shown by `shotCrop` and `shotView` in place of each screenshot.
 */
export async function loadScreens() {
  if (!SCREENS) return null;
  try {
    return JSON.parse(await fetchRepoFile(SCREENS));
  } catch (error) {
    console.error(`The screens manifest ${SCREENS} didn't load:`, error);
    return error instanceof Error ? error : new Error(String(error));
  }
}

/** What a `Shot` shows when the manifest didn't load. */
const unavailable = (error) =>
  el(
    "p",
    { class: "doc-note" },
    `Screenshot unavailable: ${SCREENS} didn't load (${error.message}).`,
  );

const imageUrl = (shot) => repoUrl(resolveHref(SCREENS, shot.image).path);
const nameOf = (shot, region) => (region ? `${shot.title}: ${region.label}` : shot.title);

/** The screenshot cropped to `region` (the whole screen when it is null), as wide as its holder up to `maxWidth` px. Null when `ref` names nothing; a note when the manifest didn't load. */
export function shotCrop(screens, ref, maxWidth = 560) {
  if (screens instanceof Error) return unavailable(screens);
  const found = resolveShot(screens, ref);
  if (found.error) return null;
  const { shot, region } = found;
  const crop = region ?? { x: 0, y: 0, w: shot.width, h: shot.height };
  // Percentages place the image against the crop's box, so the crop scales with its holder.
  const at = (offset, whole, part) => (whole === part ? 0 : (offset / (whole - part)) * 100);
  return el("div", {
    class: "crop",
    role: "img",
    "aria-label": nameOf(shot, region),
    style: [
      `max-width: ${Math.min(crop.w, maxWidth)}px`,
      `aspect-ratio: ${crop.w} / ${crop.h}`,
      `background-image: url("${imageUrl(shot)}")`,
      `background-size: ${(shot.width / crop.w) * 100}% auto`,
      `background-position: ${at(crop.x, shot.width, crop.w)}% ${at(crop.y, shot.height, crop.h)}%`,
    ].join(";"),
  });
}

/**
 * The whole screen of `ref`'s shot, each region outlined and numbered and linked to its box; the
 * list under it says what each is and links its code. The spotlight darkens the rest and lights
 * one region: the one under the pointer or keyboard focus, else the region `ref` names. Null
 * when `ref` names nothing.
 */
export function shotView(screens, ref) {
  if (screens instanceof Error) return unavailable(screens);
  const found = resolveShot(screens, ref);
  if (found.error) return null;
  const { shot, region: own } = found;
  // The pointer wins over keyboard focus, so leaving with the pointer returns to the focused region.
  let hovered = null;
  let focused = null;
  const frame = el("div", {
    class: "shot-frame",
    style: `aspect-ratio: ${shot.width} / ${shot.height}`,
  });
  const spot = el("div", { class: "shot-spot", "aria-hidden": "true" });
  const place = (region) =>
    [
      `left: ${(region.x / shot.width) * 100}%`,
      `top: ${(region.y / shot.height) * 100}%`,
      `width: ${(region.w / shot.width) * 100}%`,
      `height: ${(region.h / shot.height) * 100}%`,
    ].join(";");
  const targets = [];
  const light = () => {
    const lit = shot.regions.find((r) => r.id === (hovered ?? focused ?? own?.id));
    frame.classList.toggle("is-spot", Boolean(lit));
    spot.hidden = !lit;
    if (lit) spot.setAttribute("style", place(lit));
    for (const { region, nodes } of targets)
      for (const node of nodes) node.classList.toggle("is-hot", region === lit);
  };
  // Focus moving between a line's two links blurs then refocuses within the line, so it stays lit.
  const lights = (region) => {
    const set = (which, id) => () => {
      if (which === "hover") hovered = id;
      else focused = id;
      light();
    };
    return {
      onmouseenter: set("hover", region.id),
      onmouseleave: set("hover", null),
      onfocusin: set("focus", region.id),
      onfocusout: set("focus", null),
    };
  };
  const number = (i) => el("span", { class: "shot-number" }, i + 1);
  const outlines = shot.regions.map((region, i) => {
    const attrs = {
      class: "shot-region",
      style: place(region),
      title: region.map ? `${region.label} → ${region.map}` : region.label,
      ...lights(region),
    };
    return region.map
      ? el("a", { ...attrs, href: `#${region.map}` }, number(i))
      : el("span", attrs, number(i));
  });
  const lines = shot.regions.map((region, i) =>
    el(
      "li",
      lights(region),
      number(i),
      el(
        "span",
        { class: "shot-region-text" },
        region.map ? el("a", { href: `#${region.map}` }, region.label) : region.label,
        region.code && pathLink(region.code),
      ),
    ),
  );
  for (const [i, region] of shot.regions.entries())
    targets.push({ region, nodes: [outlines[i], lines[i]] });
  frame.append(
    el("img", {
      class: "shot-image",
      src: imageUrl(shot),
      alt: `${shot.title}, ${shot.width} by ${shot.height} pixels`,
      width: shot.width,
      height: shot.height,
    }),
    // Under the outlines, so they stay clickable; its shadow is the dimming.
    spot,
    ...outlines,
  );
  light();
  return el(
    "section",
    { class: "screen" },
    el("h3", null, `Screen: ${shot.title}`),
    frame,
    el("ol", { class: "shot-regions" }, lines),
  );
}
