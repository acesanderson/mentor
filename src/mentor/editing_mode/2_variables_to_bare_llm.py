from review_certificates import review_curriculum, learner_progression 
from mentor import Mentor
from conduit import Prompt, Model, Conduit

if __name__ == "__main__":
    topic = "Data Science with Python"
    print("Generating curriculum for", topic)
    c = Mentor(topic)
    print("Reviewing curriculum for", topic)
    critique = review_curriculum(c, "Data Scientists")
    print("\n=========\ncritique\n=========\n", critique)
    m = Model('gpt')
    p = Prompt("""
Look at this curation that an l&d specialist has made for this topic: {{topic}}.

<curation>
{{curation}}
</curation>
                    
This was critiqued by a curriculum specialist. Here is their critique:

<critique>
{{critique}}
</critique>
                    
Based on this critique, what would you change in the curation? Make a detailed list of changes, focusing entirely on the content (not learning modality).
""".strip())
    conduit = Conduit(p, m)
    response = conduit.run(input_variables = {'topic': topic, 'curation': c, 'critique': critique})
    print("\n=========\nresponse\n=========\n", response.content)
