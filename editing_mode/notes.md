### Description

"Editing mode" for Mentor is an agent that does the following:
- takes a critique from either our Curriculum Reviewer or Learner Guinea Pig, as well as Curation + the TOCs
- uses ReACT prompting to come up with a strategy to improve the Curation object, calls a function to get other TOCs if necessary, and returns an improved Curation object.

### Goal

Improve quality of curation objects for these criteria:
- comprehensiveness (covering the right topics) [curriculum review]
- scaffolding (remove things that are too advanced) [learner review]
- other parameters to keep in mind like
    - lenth (6-8 courses)
    - what else? (do we need to bring in metadata?)

### How we will get there
- import from analyze_lp: generate_curriculum (whatever that's called)
- import from review_certificates: curriculum_review, learner_review (whatever those are called)
- create these simple chains to understand how the prompts interact:
 - Mentor --curation_object--> curriculum review
 - Mentor --curation_object--> learner review
- have a bare LLM take in the following:
 - $CURATION, $TOCS, $CRITIQUE
 - and return a natural language description of how they would fix it
 - optimize that prompt for the correct understanding of what needs to be done
- turn it into agent with the RAG function
 - a "reflect" function?
 - add a "blacklist" function?
 - a "new Curation object" function that LLM is actually handling? (return <curation>[new curation object]</curation>)
