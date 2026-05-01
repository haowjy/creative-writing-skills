# Package Architecture

## Spawn Hierarchy

Who orchestrates whom. Arrows show spawn relationships.

```mermaid
graph TD
    SO["story-orchestrator<br/>(user-facing)"]

    SO -->|explores| BS[brainstormer]
    SO -->|explores| RE[researcher]
    SO -->|explores| EX[explorer]
    SO -->|explores| CS[character-sim]
    SO -->|structures| OL[outliner]
    SO -->|structures| SC[style-creator]
    SO -->|drafts| DO[draft-orchestrator]
    SO -->|records| KO[knowledge-orchestrator]
    SO -->|documents| WE[wiki-editor]

    DO -->|writes| WR[writer]
    DO -->|reviews| CR[critic]
    DO -->|reviews| CC[continuity-checker]
    DO -->|reviews| RS[reader-sim]

    KO -->|mines| SM[session-miner]
    KO -->|extracts| CH[chronicler]
    KO -->|maintains| GM[graph-maintainer]

    classDef orch fill:#4a6fa5,color:#fff
    classDef creative fill:#6b9080,color:#fff
    classDef review fill:#c17c74,color:#fff
    classDef knowledge fill:#b5838d,color:#fff

    class SO,DO,KO orch
    class BS,OL,WR,SC,WE,CS creative
    class CR,CC,RS review
    class SM,CH,GM,EX,RE knowledge
```

## Skill Dependencies

Which agents load which skills. Meridian infrastructure skills (meridian-spawn, meridian-work-coordination) omitted — all three orchestrators load both.

```mermaid
graph LR
    subgraph Orchestrators
        SO[story-orch]
        DO[draft-orch]
        KO[knowledge-orch]
    end

    subgraph Creative
        BS[brainstormer]
        OL[outliner]
        WR[writer]
        SC[style-creator]
        WE[wiki-editor]
    end

    subgraph Reviewers
        CR[critic]
        CC[continuity-checker]
        RS[reader-sim]
        CS[character-sim]
    end

    subgraph Knowledge
        SM[session-miner]
        CH[chronicler]
        GM[graph-maintainer]
        EX[explorer]
    end

    subgraph "Shared Skills"
        OR[orchestrate]
        WA[writing-artifacts]
        KG[knowledge-graph]
        WP[writing-principles]
        SCtx[story-context]
        SD[story-decisions]
        WS[writing-staffing]
        WI[writing-issues]
        MM[mermaid]
        PC[prose-critique]
    end

    subgraph "Single-Consumer Skills"
        BRS[brainstorming]
        SA[story-architecture]
        WD[wiki-docs]
        PW[prose-writing]
    end

    %% orchestrate — 3 orchestrators
    SO --> OR
    DO --> OR
    KO --> OR

    %% writing-artifacts — 6 agents
    SO --> WA
    DO --> WA
    KO --> WA
    CH --> WA
    GM --> WA
    SM --> WA

    %% knowledge-graph — 6 agents
    KO --> KG
    CH --> KG
    CC --> KG
    EX --> KG
    GM --> KG
    WE --> KG

    %% writing-principles — 5 agents
    WR --> WP
    CR --> WP
    CS --> WP
    RS --> WP
    SC --> WP

    %% story-context — 5 agents
    SO --> SCtx
    DO --> SCtx
    KO --> SCtx
    BS --> SCtx
    WR --> SCtx

    %% story-decisions — 4 agents
    SO --> SD
    DO --> SD
    KO --> SD
    SM --> SD

    %% writing-staffing — 3 orchestrators
    SO --> WS
    DO --> WS
    KO --> WS

    %% writing-issues — 3 agents
    CR --> WI
    CC --> WI
    SC --> WI

    %% mermaid — 3 agents
    OL --> MM
    GM --> MM
    WE --> MM

    %% prose-critique — 2 agents
    CR --> PC
    CC --> PC

    %% single-consumer skills
    BS --> BRS
    OL --> SA
    WE --> WD
    WR --> PW

    classDef orch fill:#4a6fa5,color:#fff
    classDef creative fill:#6b9080,color:#fff
    classDef review fill:#c17c74,color:#fff
    classDef knowledge fill:#b5838d,color:#fff
    classDef sharedSkill fill:#dda15e,color:#000
    classDef soloSkill fill:#e9c46a,color:#000

    class SO,DO,KO orch
    class BS,OL,WR,SC,WE,CS creative
    class CR,CC,RS review
    class SM,CH,GM,EX knowledge
    class OR,WA,KG,WP,SCtx,SD,WS,WI,MM,PC sharedSkill
    class BRS,SA,WD,PW soloSkill
```

## Model Routing

Cost tiers mapped to agent roles.

```mermaid
graph LR
    subgraph "opus — craft-sensitive"
        CR[critic]
        WR[writer]
        SC[style-creator]
        DO[draft-orchestrator]
    end

    subgraph "sonnet — mid-tier"
        BS[brainstormer]
        OL[outliner]
        WE[wiki-editor]
        KO[knowledge-orchestrator]
    end

    subgraph "gpt-5.4-mini — high-throughput"
        CH[chronicler]
        EX[explorer]
        GM[graph-maintainer]
        RE[researcher]
        SM[session-miner]
    end

    subgraph "gpt — deep reasoning"
        CC[continuity-checker]
    end

    subgraph "unset — needs model"
        SO[story-orchestrator]
        RS[reader-sim]
        CS[character-sim]
    end

    classDef opus fill:#4a6fa5,color:#fff
    classDef sonnet fill:#6b9080,color:#fff
    classDef mini fill:#b5838d,color:#fff
    classDef gpt fill:#c17c74,color:#fff
    classDef unset fill:#999,color:#fff

    class CR,WR,SC,DO opus
    class BS,OL,WE,KO sonnet
    class CH,EX,GM,RE,SM mini
    class CC gpt
    class SO,RS,CS unset
```

## Artifact Flow

How work products move between agents. Arrows show write → read relationships.

```mermaid
graph TD
    subgraph "work/ — temporary"
        WB["work/brainstorm/"]
        WO["work/outline/"]
        WD["work/drafts/"]
        WC["work/critique-reports/"]
    end

    subgraph "kb/ — durable"
        KS["kb/styles/"]
        KC["kb/characters/"]
        KW["kb/world/"]
        KT["kb/timeline/"]
        KCN["kb/canon/"]
        KI["kb/issues/"]
        KG["kb/graphs/"]
    end

    BS[brainstormer] -->|writes| WB
    WB -->|read by| SO[story-orchestrator]

    OL[outliner] -->|writes| WO
    WO -->|read by| WR[writer]

    WR -->|writes| WD
    WD -->|read by| CR[critic]
    WD -->|read by| RS[reader-sim]
    WD -->|read by| CC[continuity-checker]

    CR -->|writes| WC
    CC -->|writes| WC
    WC -->|read by| WR

    SC[style-creator] -->|writes| KS
    KS -->|read by| WR
    KS -->|read by| CR

    CH[chronicler] -->|writes| KC
    CH -->|writes| KW
    CH -->|writes| KT
    CH -->|writes| KCN
    SM[session-miner] -->|writes| KC
    SM -->|writes| KW

    CR -->|writes| KI
    SC -->|writes| KI
    CC -->|writes| KI

    GM[graph-maintainer] -->|writes| KG

    classDef work fill:#dda15e,color:#000
    classDef kb fill:#6b9080,color:#fff
    classDef agent fill:#4a6fa5,color:#fff

    class WB,WO,WD,WC work
    class KS,KC,KW,KT,KCN,KI,KG kb
    class BS,OL,WR,CR,RS,CC,SC,CH,SM,GM,SO agent
```

## Skill Reuse Summary

| Skill | Consumers | Notes |
|---|---|---|
| writing-artifacts | 6 | Shared artifact contract — all orchestrators + knowledge workers |
| knowledge-graph | 6 | Document navigation — knowledge workers + wiki-editor |
| writing-principles | 5 | Reader psychology + AI failure modes — all prose-touching agents |
| story-context | 5 | Context scoping — orchestrators + writer + brainstormer |
| story-decisions | 4 | Decision capture — orchestrators + session-miner |
| orchestrate | 3 | Coordination model — delegation, convergence, synthesis — orchestrators only |
| meridian-spawn | 3 | Spawn mechanics — orchestrators only |
| meridian-work-coordination | 3 | Work lifecycle — orchestrators only |
| writing-staffing | 3 | Team composition — orchestrators only |
| writing-issues | 3 | Issue tracking — critics + style-creator |
| mermaid | 3 | Diagram syntax — diagram-producing agents |
| prose-critique | 2 | Critique methodology — critic + continuity-checker |
| brainstorming | 1 | Capture conventions — brainstormer only |
| story-architecture | 1 | Structure methodology — outliner only |
| wiki-docs | 1 | Wiki conventions — wiki-editor only |
| prose-writing | 1 | Drafting technique — writer only |
