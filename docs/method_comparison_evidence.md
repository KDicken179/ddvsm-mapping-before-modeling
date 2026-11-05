# Method-comparison verification (DDVSM manuscript)

Date of check: 2026-11-05

## How this was checked, and its limits

- Direct downloads (curl) and doi.org / api.crossref.org were blocked by the session egress proxy, so no DOI was resolved through doi.org. DOI-to-paper matches below were confirmed from publisher or repository pages and full-text PDFs that print the DOI.
- Full texts were read through a web-fetch tool that extracts and returns passages from the page. Quotes below are what that tool returned as verbatim text. They were not compared character-by-character against a local copy of the PDF. Spot-check any quote before it goes into the manuscript.
- Page numbers for CRISP-DM, CRISP-ML(Q) and GQM come from the printed page numbers in the fetched PDFs. GQM page numbers came from OCR footers and may be off by one.
- Meudt et al. (2017) full text could not be accessed (ResearchGate, Semantic Scholar and ScienceDirect were blocked or failed). Its cells are based on Bega et al.'s (2023) description of it, which is a secondary source.

Legend: Yes = explicitly prescribed. Partial = touched on, but weaker or narrower than the capability (see evidence). No = not prescribed. UV = unable to verify from the primary source.

## Summary table

| Method | C1 Decision-anchored | C2 Time-ordered steps and queues | C3 Not-yet-captured variables | C4 Field-level audit vs spec | C5 Prediction-time validity / leakage | C6 Intervention lead time | C7 Go/no-go before modeling | C8 Off-system sources |
|---|---|---|---|---|---|---|---|---|
| 1. CRISP-DM 1.0 (Chapman et al., 2000) | Partial | No | Partial | Partial | No | Partial | Partial | Partial |
| 2. CRISP-ML(Q) (Studer et al., 2021) | Partial | No | Partial | Yes | No | No | Yes | No |
| 3. GQM (Basili et al., 1994) | Partial | No | Yes | No | No | No | No | No |
| 4. GR4ML (Nalchigar & Yu, 2018; Nalchigar et al., 2021) | Yes | Partial | Partial | Partial | No | Partial | No | No |
| 5a. VSM 4.0 (Meudt et al., 2017) | UV | UV (secondary: Yes) | UV (secondary: Partial) | UV | UV (secondary: No) | UV | UV | UV (secondary: Yes) |
| 5b. VSM 4.0 plus (Bega et al., 2023) | No | Partial | Partial | No | No | Partial | No | Yes |
| 6. Rokoss et al. (2024) | Partial | Partial | Partial | Partial | Yes | Yes | No | Partial |
| 7. Data Readiness Levels (Lawrence, 2017) | Partial | No | Partial | Partial | No | No | Partial | Partial |

## Per-cell evidence

### 1. CRISP-DM 1.0 Step-by-step data mining guide

Source read: full PDF (SMU-hosted copy of CRISPWP-0800). Business Understanding and Data Understanding sections were complete in the fetched text.

- C1 Partial. Anchors work to business objectives and business questions, not to specific operational decisions. User guide 1.1: "Specify expected benefits in business terms." Reference model 1.1: "Describe the customer's primary objective, from a business perspective." The only "decision" sentences concern the project itself (p. 14 and p. 31), not operational decisions the model serves.
- C2 No. No process map or step/queue representation of the business operation. The only process-sequence text is the project plan, "together with duration, resources required, inputs, outputs and dependencies" (reference model 1.4), which describes the data-mining project, not the value stream.
- C3 Partial. Asks whether needed information exists and how to get missing attributes, but does not prescribe specifying uncaptured variables. User guide 2.1, p. 43: "Check if all the information needed (to solve the data mining goals) is actually available." p. 44: "How can missing attributes be acquired?" Also 1.2 Costs: "Estimate costs for data collection."
- C4 Partial. Attribute-level checks against goals and requirements exist, but there is no derived variable specification to audit against. Reference model 2.2: "Does the data acquired satisfy the relevant requirements?" User guide 2.2, p. 44: "Check accessibility and availability of attributes." and "Is the attribute relevant for the specific data mining goal?" User guide 2.4, p. 46: "Identify missing attributes and blank fields."
- C5 No. Leakage and prediction-time availability are not addressed in Business or Data Understanding. Closest text is about history length, 2.1, p. 43: "Think about how long history one should use even if available."
- C6 Partial. One advisory example, not a test. User guide 1.3, p. 41: "It may be wise to re-define the problem." followed by "modeling product retention rather than customer retention" "since targeting customer retention may be too late to affect the outcome!"
- C7 Partial. The plan should "Mark decision points." (user guide 1.4, p. 42) and the reference model calls for "a review of progress and achievements" at the end of each phase (1.4). The explicit proceed decision is in Evaluation (p. 31: "Describe the decision as to how to proceed along with the rationale."), which comes after modeling.
- C8 Partial. Prompts identification of non-electronic sources but does not record them per variable. User guide 1.2, p. 37: "Identify type of data sources (on-line sources, experts, written documentation, etc.)." User guide 2.1, p. 44: "some knowledge about the data may be on non-electronic sources (e.g., People, Printed text, etc.)." No mention of spreadsheets (keyword not found).

### 2. CRISP-ML(Q) (Studer et al., 2021)

Source read: published PDF (make-03-00020-v3.pdf) from the TU Berlin DepositOnce repository. Text was complete through the reference list.

- C1 Partial. Business objectives and success criteria, not decisions. §3.1, p. 396: "define the business objectives and translate it to ML objectives". §3.1.2, p. 397: "Define the purpose and the success criteria of the ML application from a business point of view".
- C2 No. No business process, step or queue representation in §3.1 or §3.2.
- C3 Partial. Acknowledges data may need to be collected, but does not prescribe identifying specific uncaptured variables. §3.1.4, p. 398: "A ML project might be delayed until the data is collected". §3.1.3, p. 397: "a major source of project delays is the lack of data availability".
- C4 Yes. Field-level data requirements and checks. §3.1.5, p. 398: "the expected feature values (a range for continuous features or a list for discrete features)" and "Documentation of the data requirements could be expressed in the form of a schema". p. 399: "the production data has to be checked according to the requirements". The specification is a value-range schema, not one derived from decisions.
- C5 No. Not addressed in §3.1 or §3.2. §3.4, p. 403 warns about "information from a test set leak into the validation or even training set", which is train/test contamination during modeling, not prediction-time validity of fields.
- C6 No. "latency", "inference time" and "time constraint" not found. "Requirements on the application" lists "robustness, scalability, explainability, and resource demand" (§3.1.3, p. 398).
- C7 Yes. Feasibility gate in §3.1.3, p. 398: "the ML project should be terminated or put on hold at this stage" (when sample size is insufficient). §3.1.2, p. 397: paths to "redefine objectives in an earlier phase, stop, or postpone the project".
- C8 No. Spreadsheets, manual logs or non-system sources not found. The only format mention is CSV as a file standard (§3.2.4, p. 400).

### 3. Goal Question Metric (Basili, Caldiera & Rombach, 1994)

Source read: full text PDF hosted at cs.umd.edu (gqm.pdf). The PDF prints title and authors but no venue, publisher or year.

- C1 Partial. Top-down goal to question to metric derivation, but goals are measurement goals, not operational decisions. §2, p. 4: "starting with a goal (specifying purpose of measurement, object to be measured, issue to be measured, and viewpoint". The fetch found no mention of decisions or decision-making. §1, p. 1 frames measurement as supporting "corrective action".
- C2 No. Processes are a measurement object ("Software related activities normally associated with time", §2, p. 3) and §3, p. 6 says "we need a model of that process", but no time-ordered step/queue representation is prescribed.
- C3 Yes. Measures are specified top-down from questions, independent of existing data. §3, p. 5: "specifying the measures that need to be collected in order to answer those questions".
- C4 No. Existing data is a selection consideration (§3, p. 7: "maximize the use of existing" "data sources if they are available and reliable"), not an audit of a dataset against the metric definitions.
- C5 No. Not addressed.
- C6 No. Not addressed.
- C7 No. Only a "relevancy analysis step before completing our list of goals" (§3, p. 6), which screens goals, not data readiness.
- C8 No. §3, p. 8: "select the appropriate data collection techniques, tools and procedures" with no named off-system sources.

### 4. GR4ML / business-driven data analytics (Nalchigar & Yu, 2018; Nalchigar, Yu & Keshavjee, 2021)

Sources read: author-hosted PDFs of both papers (cs.toronto.edu/~soroosh/papers). DKE 2018 text complete (figures partly garbled). RE 2021 text complete apart from OCR damage in figures and a truncated final appendix question.

- C1 Yes. DKE 2018 §3.1 defines Decision Goals as "intention of an actor for taking actions towards achieving strategic goals" and Question Goals as capturing "the 'needs-to-know' of an actor". RE 2021 §2: "how Business Goals are refined into Decision Goals and Question Goals".
- C2 Partial. No business-process or queue construct in the DKE framework. The only sequence is in data preparation: "Operators are linked by Data Flows to represent the sequence and dependency." (DKE §3.3). RE 2021 Appendix A asks "Which business (routine) process is this decision part of?" but does not model steps or waits.
- C3 Partial. Observed, not prescribed. RE 2021 §4: "their existing data assets did not (yet) include the data for generating the Insight element at hand". DKE 2018 data view describes existing sources; no step for specifying uncaptured variables. "availability" does not appear in DKE 2018.
- C4 Partial. Required attributes are specified from existing assets, with no audit procedure. RE 2021 §4: "specify what data attributes (from their existing data assets) would be required" and modelers "reviewed Entity Relationship Diagram (ERD) documents and data dictionaries". Appendix A: "What data attributes (i.e., features), in what format, and aggregation level are needed".
- C5 No (not prescribed). The RE 2021 case model (Fig. 10, OCR) contains one case-specific filter, "Remove all the rows where sBP is collected aer an event...", but the framework does not prescribe a prediction-time validity test, and "leakage" is not found.
- C6 Partial. Insight attributes include timing descriptors (DKE §3.1: "Type, Input, Output, Usage Frequency, Update Frequency, and Learning Period") and an example with "Alerts (8 h in advance)" (DKE §2). No test of whether predictions arrive in time to act.
- C7 No. DKE §2 mentions analyzing "satisfiability of softgoals during early phases of design", which is not a data-readiness go/no-go. DKE §7 states a step-by-step methodology is future work.
- C8 No. Spreadsheets, paper and manual records not found. Data sources discussed are IT systems (RE 2021 §7: "data available in health IT systems").

### 5a. Value Stream Mapping 4.0 (Meudt, Metternich & Abele, 2017)

Primary source NOT accessed. All cells are UV. The following is secondary, from Bega et al. (2023) §3 and §5.1, and is not verification of the original:
- Extends classic VSM at the process-step level: "enlarges the classic VSM with options for gathering process steps' data points" and "disaggregate the rough information needed for a single process step into multiple data points".
- Data points characterized by "frequency and type of recording and actual value".
- Records storage medium "(e.g., paper, employees, software systems as enterprise resource planning)" (supports C8 Yes if confirmed in the original).
- Records "the usage of a data point (e.g., for shopfloor management (SFM) or process control)" (usage, not decisions).
- Bega et al.: "VSM 4.0 only focuses on a more business perspective, so the methodology lacks technical implementation".

### 5b. VSM 4.0 plus (Bega et al., 2023)

Source read: Springer article page (full text, figures and Table 1 not rendered).

- C1 No. "Decision" appears only as motivation (Abstract: "data-based decision-making"). Data use is captured as type of use and application (e.g., an OEE KPI in shopfloor management, §5.2 SC 8), not decisions.
- C2 Partial. Built on classic VSM process steps. §5.3: "Both approaches involve performing the classic value stream analysis at the beginning". §5.1: "illustrates the enhancement of one process step from the classic VSM." The terms "inventory", "lead time" and "material flow" were not found in the text, so queues are not explicit in this paper.
- C3 Partial. Gaps surface as findings, not as a variable specification. §6.1: "Data graveyards, further processing inconsistencies, and media breakage are revealed and made transparent." Intro (motivation): "relevant information is missing."
- C4 No. Per-data-point properties (accuracy, unit, communication protocol) are documented (§5.2 SC 1) but there is no audit of a candidate modeling dataset.
- C5 No. The paper does not address predictive models.
- C6 Partial. §5.2 SC 4: "the frequency of importing data points is to factor, especially when it differs from the frequency of recording." No intervention lead-time test.
- C7 No. §5.3: "primarily conceived as a tool for analysis and not for design purpose."
- C8 Yes. §6.1: "information transfer on sight or through paper". §6.2: "data is collected manually via the MES terminal or via the medium paper." Distinguishes "automated, semi-automated, and manually" recorded data (§5.2 SC 2). Spreadsheets/Excel not mentioned.

### 6. Rokoss et al. (2024)

Source read: Springer article page (full text through the Discussion, remainder read via a second pass; conclusion partly seen).

- C1 Partial. Target is tied to one decision context (delivery date at order confirmation/offer), but there is no general decision-to-variable derivation. Comparison section: "the key objective in the given case studies is predicting the delivery date of a customer order". Intro: "companies face the choice of delaying the confirmation of the customer order or adding significant buffers".
- C2 Partial. Business and data understanding: "identify the key stages of the ordering process" and "Timestamps marking the start and finish of every machining step internally are necessary". Waiting appears through WIP ("the workload that is waiting to be processed by a system", data preparation). VSM is suggested only for external processes: "the relevance of external manufacturing processes needs to be examined using value stream mapping and/or interviews."
- C3 Partial. "interviews with stakeholders allow to unveil domain knowledge" (business and data understanding). Missing variables are reported as findings: "the transition times (not available in the observed cases)" (discussion), not specified as a prescribed step.
- C4 Partial. Table 3 caption: "Main data groups and availability in time". This is a data-group level check of availability timing, not a field-level audit against a specification.
- C5 Yes. Business and data understanding: data "needs to be split into data that is available prior to the processing by the process planning department." Modeling warns of "look-ahead bias" "when future data is used during training", handled with time-series split cross-validation.
- C6 Yes. Evaluation: "predicting the delivery date either when the first offer is made or shortly before" order confirmation. Later text: "Only the first two of these three groups are available for a first offer or as the customer order is received".
- C7 No. No explicit feasibility or go/no-go decision before modeling found.
- C8 Partial. Data preparation: "measured manually by operators, who observe processes and record timestamps" and "This manual process ultimately often leads to gaps in the collected data." Spreadsheets and paper not mentioned. Not prescribed as a recording step.

### 7. Data Readiness Levels (Lawrence, 2017)

Source read: arXiv PDF, arXiv:1705.02245v1 [cs.DB].

- C1 Partial. Band A requires a task or question, not an operational decision. §2.3: "A data set can only be considered in Band A once a task is defined." and "it is only when you have the question you wish to answer".
- C2 No. No process representation.
- C3 Partial. §2.3: "There may be a realisation that new data needs to be actively collected to get the answers required." No specification step.
- C4 Partial. Representation checks, not against a specification. §2.2: "How are missing values handled, what is their encoding?" and "for manual data are there data entry errors?"
- C5 No. Leakage, temporal ordering and prediction-time availability not found.
- C6 No. Not addressed (only project-time overruns, Abstract).
- C7 Partial. Levels are used as gating language in illustrative quotes, e.g. "we'll be unable to deliver on that integration unless the data readiness level is at least B3" (§2) and "My team will be ineffectual until it's B1" (§3.1). No formal go/no-go procedure.
- C8 Partial. Band C considers recording format: "the format in which it's being recorded (e.g. handwritten log book, stored in PDF format or old machine formats)" (§2.1), and §2.2 asks whether data "has been through a spreadsheet software". Assesses accessibility rather than recording off-system sources per variable.

## Reference check

DOIs could not be resolved through doi.org (blocked). Matches were confirmed as follows.

| Ref | Status | Evidence | Discrepancies / notes |
|---|---|---|---|
| CRISP-DM 1.0 | Confirmed (title, authors, year) | PDF title page | Seven authors: Chapman, Clinton, Kerber, Khabaza, Reinartz, Shearer, Wirth. Dated August 2000, copyright 1999 and 2000. Issued by the CRISP-DM consortium (SPSS distributed it). Citing "SPSS" as publisher is common but the document itself is a consortium publication. No DOI. |
| Studer et al. 2021 | Confirmed | Published PDF prints "Mach. Learn. Knowl. Extr. 2021, 3, 392–413. https://doi.org/10.3390/make3020020"; repository record gives issue 2 | Seven authors: Studer, Bui, Drescher, Hanuschkin, Winkler, Peters, Müller. Matches. |
| Basili, Caldiera & Rombach 1994 | Partly confirmed | Title and authors from the cs.umd.edu PDF; Wikipedia gives year 1994 | The PDF prints no venue, publisher, year or pages. "Encyclopedia of Software Engineering" (Wiley) could not be confirmed from any primary or publisher source. UMIACS lists it with an unrelated venue (ISESE'06, 2006), which looks like a database error. Unable to verify editor, publisher and pages. |
| Nalchigar & Yu 2018 | Confirmed | Author PDF prints Data & Knowledge Engineering 117, 359–372, DOI 10.1016/j.datak.2018.04.006 | Request gave no volume/pages. Add 117, 359–372. |
| Nalchigar, Yu & Keshavjee 2021 | DOI and title confirmed; volume/pages from secondary source | Author PDF prints DOI 10.1007/s00766-020-00343-z (received 19 Nov 2019, accepted 15 Nov 2020) but no volume/pages. Volume 26(2), 237–254, June 2021 confirmed only via reference [34] in arXiv:2210.00859. | Title: "Modeling machine learning requirements from three perspectives: a case report from the healthcare domain". The publisher page was blocked. |
| Meudt, Metternich & Abele 2017 | Secondary only | Bega et al. (2023) reference list: "CIRP Ann 66:413–416. https://doi.org/10.1016/j.cirp.2017.04.005" | Title: "Value stream mapping 4.0: Holistic examination of value stream and information logistics in production". Issue number (1) not confirmed. Primary source not accessed. |
| Bega et al. 2023 | Confirmed | Springer page and RWTH repository record | Production Engineering 17(6), 915–927, DOI 10.1007/s11740-023-01207-5. Seven authors: Bega, Sapel, Ercan, Schramm, Spitz, Kuhlenkötter, Hopmann. Title: "Extension of value stream mapping 4.0 for comprehensive identification of data and information flows within the manufacturing domain". |
| Rokoss et al. 2024 | Confirmed | Springer page and RePEc record | JIM 35(8), 3937–3958, DOI 10.1007/s10845-023-02290-2. Six authors: Rokoss, Syberg, Tomidei, Hülsing, Deuse, Schmidt. Title: "Case study on delivery time determination using a machine learning approach in small batch production companies". Note the title is a case study; describing it as "adapted CRISP-DM" is supported by the text ("specify the very broad CRISP-DM for the task of delivery time forecasting"). Deployment phase is excluded from their adaptation. |
| Lawrence 2017 | Confirmed | arXiv PDF | arXiv:1705.02245v1 [cs.DB]; paper dated 6 April 2017, arXiv stamp 5 May 2017. Single author, Neil D. Lawrence. |

## Could not verify

1. Meudt et al. (2017): no access to the full text. All eight cells are UV. Bibliographic details come only from Bega et al.'s reference list.
2. GQM venue details (Encyclopedia of Software Engineering, editor, publisher, pages). Title, authors and content were verified.
3. Nalchigar et al. (2021) volume, issue and pages: confirmed only through a secondary reference list.
4. No DOI was resolved through doi.org. Matches rest on publisher or repository pages and PDFs that print the DOI.
5. Bega et al. (2023) Fig. 8 and Table 1 (the procedure figure and the Meudt/Lewin procedure comparison) were not rendered, so procedure steps shown only in those figures could not be checked.
6. Quotes came through a web-fetch extraction tool, not a local PDF copy. Spot-check before final use.
