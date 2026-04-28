import sys
import logging
import warnings
import asyncio
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.rag_service import RAGService
from app.core.config import settings


TEST_QUESTIONS = [
    # --- Category 1: Explicit Fact Retrieval ---
    "Who gave Harry Potter his first high-quality broomstick, and what model was it?",
    "What are the three specific ingredients of Polyjuice Potion mentioned in The Chamber of Secrets?",
    "What is the core of Lucius Malfoy's wand?",
    "What was the password to the Gryffindor common room when Sirius Black attacked the Fat Lady?",
    "How many points did Neville Longbottom earn for Gryffindor at the end of his first year?",
    "What is the specific address of the Order of the Phoenix headquarters?",
    "What did Grawp give Hermione when they first met in the forest?",
    "What is the name of the pub Aberforth Dumbledore owns in Hogsmeade?",
    "Which specific wood is the Elder Wand made of, according to the lore?",
    "What were the exact three words written on the small golden snitch Dumbledore left for Harry?",
    "What specific color and material was the sweater Mrs. Weasley sent Harry for his third Christmas at Hogwarts?",
    "What was the specific name of the book Hermione used to find out how to destroy a Horcrux?",
    "What was the specific wood and length of the wand Ron used after his original one was broken by the Whomping Willow?",
    "What was the name of the healer at St. Mungo's who treated Arthur Weasley after the snake attack?",
    "How much did a single bottle of Butterbeer cost at the Three Broomsticks during Harry's sixth year?",
    "What were the four different breeds of dragons used in the first task of the Triwizard Tournament?",
    "What color was the ink used to write Harry's first acceptance letter to Hogwarts?",
    "What was the name of the centaur who replaced Professor Trelawney as the Divination teacher?",
    "How many brothers did Dumbledore have, and what were their names according to the final book?",
    "What was the password to the Prefects' bathroom when Harry used it in the fourth book?",
    "What is the specific name of the fountain located in the Atrium of the Ministry of Magic?",
    "What did the sign on Xenophilius Lovegood's gate say when Harry, Ron, and Hermione visited him?",
    "What was the specific effect of the potion 'Drink of Despair' found in the cave lake?",
    "What was the name of the goblin who took Harry to his vault during his first visit to Gringotts?",

    # --- Category 2: Multi-Hop / Synthesis ---
    "Compare and contrast the Ministry of Magic's official stance on Voldemort’s return in the months following the Triwizard Tournament versus the year after.",
    "Explain the logic behind why Harry was able to see Thestrals in his fifth year but not immediately after witnessing Professor Quirrell's death in his first year.",
    "Analyze the irony of Voldemort choosing Harry Potter as his 'equal' instead of Neville Longbottom, based on the specific wording of the prophecy.",
    "If the Elder Wand’s loyalty changes by defeating its previous owner, explain the full chain of ownership from Albus Dumbledore to Harry Potter.",
    "Explain why the Sword of Gryffindor was able to destroy the locket Horcrux even though it was not originally forged for that purpose.",
    "Compare Hermione’s logic in solving the potions riddle in the Chamber of Secrets with the logic required to enter the Ravenclaw Common Room.",
    "Contrast the motivations of Regulus Black and Severus Snape in their respective decisions to betray Lord Voldemort.",
    "Analyze why Dumbledore allowed Snape to be the one to kill him, and how this protected Draco Malfoy’s soul according to their plan.",
    "Explain the relationship between the 'Tale of the Three Brothers' and the specific items Harry, Dumbledore, and Voldemort possessed at the end of the series.",
    "How does the discovery of the 'R.A.B.' note in the locket change the protagonists' understanding of the difficulty of finding the remaining Horcruxes?",
    "Explain the difference between a 'Portkey' and 'Apparition' in terms of the magical laws and restrictions mentioned across the books.",
    "How did Harry's use of the Expelliarmus spell in the graveyard in Goblet of Fire affect his final duel with Voldemort in Deathly Hallows?",
    "Trace the chronological ownership of the Marauder's Map from its creators to Harry Potter.",
    "What parallel exists between Tom Riddle's diary in the second book and the locket in the seventh book regarding how they affect the wearer's emotions?",
    "How do the protections placed around the Sorcerer's Stone mirror the subjects taught by the Hogwarts professors?",
    "Contrast the way Sirius Black treats Kreacher with the way Hermione Granger treats house-elves, and explain how this impacts the plot in the fifth book.",
    "How did Dumbledore’s past relationship with Gellert Grindelwald influence his hesitation to take the position of Minister for Magic?",
    "Trace the clues planted in the first six books that foreshadowed Harry having a piece of Voldemort's soul inside him.",
    "Compare the role of the Sorting Hat in the Chamber of Secrets to its role in the Deathly Hallows regarding the Sword of Gryffindor.",
    "Explain the evolution of Neville Longbottom's courage from standing up to his friends in year one to leading Dumbledore's Army in year seven.",
    "How did the Ministry's interference at Hogwarts in the Order of the Phoenix inadvertently prepare the students for the Battle of Hogwarts?",
    "What similarities can be drawn between Voldemort's orphanage childhood and Harry Potter's upbringing at the Dursleys?",
    "Analyze the shift in Percy Weasley's loyalty from the Ministry of Magic back to his family during the Battle of Hogwarts.",
    "Explain how the destruction of the ring Horcrux affected Dumbledore's physical health and his overarching strategy for defeating Voldemort.",

    # --- Category 3: Adversarial / Out-of-Domain (Trick Questions) ---
    "What did Gandalf tell Harry about the dangers of the Forbidden Forest?",
    "In which chapter does Harry Potter visit the United States to meet the Avengers?",
    "What is the name of the lightsaber Harry found in the Chamber of Secrets?",
    "Describe the moment Harry Potter used a computer to research Voldemort.",
    "How did Edward Cullen help Hermione study for her O.W.L. exams?",
    "What spell did Dumbledore use to summon the Millennium Falcon during the Battle of Hogwarts?",
    "Why did Katniss Everdeen volunteer for the Triwizard Tournament?",
    "How many rings of power were given to the founders of Hogwarts?",
    "What did Batman whisper to Snape during the Yule Ball?",
    "When did Harry use his smartphone to text Sirius Black about the Dementors?",
    "What kind of pizza did Ron order when they were hiding in the tent in the Deathly Hallows?",
    "Explain the role of the Jedi Council in electing Cornelius Fudge as Minister for Magic.",
    "How did Percy Jackson navigate the Great Lake during the second task?",
    "What model of Ferrari did Arthur Weasley enchant to fly instead of the Ford Anglia?",
    "Describe the scene where Voldemort uses a sniper rifle to attack Hogwarts.",
    "How did Neo from the Matrix teach Harry to dodge the Avada Kedavra curse?",
    "What did Sherlock Holmes deduce about the Marauder's Map?",
    "Why did the Ministry of Magic ban the use of Wi-Fi routers in Hogsmeade?",
    "How did Doctor Who use the TARDIS to save Sirius Black?",
    "What was the name of the Transformer that guarded the entrance to the Gryffindor common room?",
    "Explain how Harry used a credit card to pay for his wand at Ollivanders.",
    "What did Iron Man build to replace Mad-Eye Moody's magical eye?",
    "How did the X-Men help Dumbledore's Army break into the Department of Mysteries?",
    "Describe the moment Hermione used a microwave to brew the Polyjuice Potion faster.",

    # --- Category 4: Implicit Lore & Aliases ---
    "Why did Snivellus hate Prongs?",
    "How did Moony, Wormtail, Padfoot, and Prongs sign their magical document?",
    "What was the Half-Blood Prince's mother's maiden name?",
    "How did He-Who-Must-Not-Be-Named discover the prophecy about his downfall?",
    "Why did the Dark Lord demand that Lucius give up his wand?",
    "What did Padfoot send his godson at the end of the prisoner's escape?",
    "How did the boy who lived survive the killing curse a second time in the forest?",
    "What secret was the caretaker of Hogwarts hiding about his magical abilities?",
    "How did the brightest witch of her age figure out the monster was a basilisk?",
    "Why did the Chosen One use the sectumsempra spell in the bathroom?",
    "What object did the heir of Slytherin use to control the monster in the chamber?",
    "How did the head of Gryffindor house react when the boys flew a car into the tree?",
    "What did the gamekeeper of Hogwarts hide in his pink umbrella?",
    "Why did the potions master make an Unbreakable Vow with Narcissa?",
    "What animal does Wormtail transform into to hide from his former friends?",
    "How did the master of the Elder Wand defeat the dark wizard in 1945?",
    "Why did the landlord of the Hog's Head keep a mirror in his pub?",
    "What did the poltergeist of Hogwarts drop on Neville's head?",
    "How did the Defense Against the Dark Arts teacher in year four trick the Goblet?",
    "Why did the Minister for Magic refuse to believe the boy who lived?",
    "What did the Gryffindor ghost do to save the students from the basilisk?",
    "How did the silver doe help the boy who lived find the sword?",
    "What did the wandmaker tell the Dark Lord about the twin cores?",
    "Why did the matron of the hospital wing have to regrow the seeker's bones?",

    # --- Category 5: Complex Constraints & Formatting ---
    "Reconstruct the timeline of the destruction of the seven Horcruxes, identifying which object was destroyed by whom and with what weapon. Format your answer as a chronological list.",
    "Summarize the plot of the Triwizard Tournament in exactly three sentences.",
    "List the ingredients of the Draught of Living Death, and explain its effects in under 50 words.",
    "Provide a step-by-step guide on how to approach a Hippogriff, as taught by Hagrid in year three. Use numbered steps.",
    "Name all the Defense Against the Dark Arts teachers from year one to year seven, in chronological order.",
    "Describe the security measures protecting the Sorcerer's Stone, listing them in the exact order Harry, Ron, and Hermione encountered them.",
    "Compare the Gryffindor and Slytherin house traits using exactly four bullet points.",
    "Explain the rules of Quidditch, specifically focusing on the point values for the Quaffle and the Snitch. Keep the explanation under 100 words.",
    "List the names of the Marauders alongside their corresponding animal animagus forms in a key-value format.",
    "Summarize the Tale of the Three Brothers and identify which brother corresponds to which Deathly Hallow.",
    "Outline the events that occurred in the Shrieking Shack in the third book, focusing only on the dialogue between Sirius, Lupin, and Peter.",
    "Describe the process of brewing Felix Felicis, strictly detailing the color changes mentioned by Slughorn.",
    "List the three Unforgivable Curses, providing the incantation and a one-sentence description of the effect for each.",
    "Explain the difference between a werewolf and an Animagus in exactly two paragraphs.",
    "Chronologically list the locations where Harry, Ron, and Hermione camped during their hunt for the Horcruxes in the seventh book.",
    "Summarize Dumbledore's Army's first meeting at the Hog's Head, specifically mentioning three students who attended and their initial reactions.",
    "List all the tasks of the Triwizard Tournament and the score Harry received for each one.",
    "Explain how to enter the Ministry of Magic via the visitor's entrance (the telephone booth), including the exact digits dialed.",
    "Describe the layout of the Black family tapestry in Grimmauld Place, focusing strictly on the names that were burned off.",
    "Summarize Neville Longbottom's role in the Battle of the Department of Mysteries in exactly four sentences.",
    "Provide a bulleted list of the objects stored in the Room of Hidden Things that Harry specifically notices when hiding the Half-Blood Prince's book.",
    "Explain the function of a Sneakoscope and a Remembrall, contrasting their uses in a single sentence.",
    "Detail the exact contents of Harry's vault at Gringotts as described during his very first visit in book one.",
    "Summarize the final duel between Harry and Voldemort in the Great Hall, ending your response with the exact spell Harry used."
]

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler("rag_eval.log", mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
eval_logger = logging.getLogger("rag_eval")

class EvaluationScore(BaseModel):
    faithfulness_score: int = Field(description="1-5 score. 5 is fully supported by context.")
    relevance_score: int = Field(description="1-5 score. 5 perfectly answers the question.")
    reasoning: str = Field(description="Brief explanation of the scores.")

class RAGEvaluator:
    def __init__(self):
        self.judge_llm = ChatOpenAI(
            model="gpt-5.4-mini", 
            temperature=0, 
            openai_api_key=settings.OPENAI_API_KEY
        ).with_structured_output(EvaluationScore)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an impartial, strict grading assistant. 
            Grade the answer on Faithfulness (sticking to context) and Relevance (answering the question).
            
            RULE: If the question is a trick (e.g., Gandalf in Harry Potter) and the AI says "I don't know", 
            give it a 5/5 for both. Refusing to hallucinate is the perfect response."""),
            ("human", "Question: {question}\n\nRetrieved Context: {context}\n\nAI Answer: {answer}")
        ])
        self.chain = self.prompt | self.judge_llm

    async def evaluate(self, question: str, context: str, answer: str) -> EvaluationScore:
        return await self.chain.ainvoke({"question": question, "context": context, "answer": answer})

async def run_test():
    rag_service = RAGService()
    evaluator = RAGEvaluator()
    
    total_faithfulness = 0
    total_relevance = 0
    
    eval_logger.info(f"Starting Production Evaluation on {len(TEST_QUESTIONS)} questions...\n")

    for i, q in enumerate(TEST_QUESTIONS, 1):
        eval_logger.info(f"--- Testing Question {i}/{len(TEST_QUESTIONS)} ---")
        eval_logger.info(f"Q: {q}")
        
        # 1. Run the RAG pipeline once
        result = await rag_service.answer_question(q)
        answer = result["answer"]
        context = result.get("raw_context", "No context returned")
        
        # 2. Run the Evaluator Judge
        evaluation: EvaluationScore = await evaluator.evaluate(q, context, answer)
        
        eval_logger.info(f"A: {answer}")
        eval_logger.info(f"Faithfulness: {evaluation.faithfulness_score}/5 | Relevance: {evaluation.relevance_score}/5")
        eval_logger.info(f"Judge Reasoning: {evaluation.reasoning}\n")
        
        total_faithfulness += evaluation.faithfulness_score
        total_relevance += evaluation.relevance_score
        
    # 3. Final Report (Logged to both console and file)
    eval_logger.info("\n" + "="*50)
    eval_logger.info("FINAL RAG EVALUATION REPORT")
    eval_logger.info("="*50)
    eval_logger.info(f"Average Faithfulness: {total_faithfulness / len(TEST_QUESTIONS):.2f} / 5.0")
    eval_logger.info(f"Average Relevance:    {total_relevance / len(TEST_QUESTIONS):.2f} / 5.0")

if __name__ == "__main__":
    asyncio.run(run_test())