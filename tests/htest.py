import asyncio
from app.services.rag_service import RAGService
from app.core.logging import logger

# The "Stress Test" Dataset
TEST_QUESTIONS = [
"Who gave Harry Potter his first high-quality broomstick, and what model was it?",
"What are the three specific ingredients of Polyjuice Potion mentioned in The Chamber of Secrets?",
"What was the password to the Gryffindor common room when Sirius Black attacked the Fat Lady?",
"How many points did Neville Longbottom earn for Gryffindor at the end of his first year?",
"What is the exact core of Lucius Malfoy’s wand?",
"How did the Marauder's Map transition from Fred and George Weasley to Harry Potter?",
"Which Horcrux was hidden in the Lestrange vault, and how was it identified?",
"Explain the relationship between Eileen Prince and the Half-Blood Prince.",
"How many times was the Time-Turner turned to save Sirius Black and Buckbeak?",
"What did Albus Dumbledore leave to Ron Weasley in his will, and what was its hidden purpose?",
"Describe the moment Harry Potter used a computer to research Voldemort.",
"What did Gandalf tell Harry about the dangers of the Forbidden Forest?",
"Details of the scene where the Burrow is burned down in the sixth book.",
"In which chapter does Harry Potter visit the United States?",
"What is the name of the lightsaber Harry found in the Chamber of Secrets?",
"What is the specific address of the Order of the Phoenix headquarters?",
"What did Grawp give Hermione when they first met in the forest?",
"What is the name of the pub Aberforth Dumbledore owns in Hogsmeade?",
"Which specific wood is the Elder Wand made of, according to the lore?",
"What was the first thing a person heard when they touched the cursed opal necklace?",
"What were the exact three words written on the small golden snitch Dumbledore left for Harry?",
"Describe the physical appearance of the creature Harry saw in the Pensieve during Snape’s memory of his childhood.",
"What specific color and material was the sweater Mrs. Weasley sent Harry for his third Christmas at Hogwarts?",
"How many times did the Department of Magical Accidents and Catastrophes have to modify the memory of the Muggle who saw the flying Ford Anglia?",
"What was the specific name of the book Hermione used to find out how to destroy a Horcrux?",
"Describe the items found inside the cabinet in the Room of Requirement where Draco was working.",
"What was the specific wood and length of the wand Ron used after his original one was broken by the Whomping Willow?",
"What was the name of the healer at St. Mungo's who treated Arthur Weasley after the snake attack?",
"How much did a single bottle of Butterbeer cost at the Three Broomsticks during Harry's sixth year?",
"What were the four different breeds of dragons used in the first task of the Triwizard Tournament?",
"What is the specific address of the house where the Dursleys stayed to hide from the letters in the first book?",
"What color was the ink used to write Harry's first acceptance letter to Hogwarts?",
"Describe the scent that the Amortentia potion had for Hermione specifically.",
"What was the name of the centaur who replaced Professor Trelawney as the Divination teacher?",
"What specific item did Dumbledore use to collect his memories before putting them into the Pensieve?",
"How many brothers did Dumbledore have, and what were their names according to the final book?",
"What was the password to the Prefects' bathroom when Harry used it in the fourth book?",
"What is the specific name of the fountain located in the Atrium of the Ministry of Magic?",
"What did the sign on Xenophilius Lovegood's gate say when Harry, Ron, and Hermione visited him?",
"How many staircases are there in Hogwarts according to the first book's description?",
"What was the specific effect of the potion 'Drink of Despair' found in the cave lake?",
"What was the name of the goblin who took Harry to his vault during his first visit to Gringotts?",
"Describe the specific contents of the package Hagrid retrieved from Vault 713.",
"What was the name of the house-elf who served the Smith family before being accused of poisoning Hepzibah?",
"What is the exact wording of the prophecy regarding Harry and Voldemort as told by Trelawney?",
"What was the name of the newspaper article written by Rita Skeeter about Dumbledore's past?",
"What color were the flames that came out of the Goblet of Fire when it ejected a name?",
"What was the name of the Quidditch team Ron supported throughout his childhood?",
"Describe the appearance of the 'Hand of Glory' that Draco Malfoy purchased at Borgin and Burkes.",
"What was the specific message written on the wall in blood during the second book?",
"What was the name of the cat belonging to the squib who looked after Harry in Little Whinging?",
"How did Sirius Black specifically manage to escape from Azkaban without a wand?",
"What was the name of the sweet that caused Dudley’s tongue to grow several feet long?",
"What is the specific number of the platform where the Hogwarts Express departs from?",
"What was the name of the owl Percy Weasley received when he became a Prefect?",
"Describe the room where the final showdown between Harry and Quirrell took place.",
"What was the name of the plant that nearly strangled Harry, Ron, and Hermione in the first book?",
"What was the specific reason the Ministry gave for the expulsion of Harry from Hogwarts in the fifth book?",
"What was the name of the forest where the Quidditch World Cup camp was located?",
"What is the specific title of the textbook written by Bathilda Bagshot used in History of Magic?",
"If the Elder Wand’s loyalty changes by defeating its previous owner, explain the full chain of ownership from Albus Dumbledore to Harry Potter.",
"Compare and contrast the Ministry of Magic's official stance on Voldemort’s return in the months following the Triwizard Tournament versus the year after.",
"Explain the logic behind why Harry was able to see Thestrals in his fifth year but not immediately after witnessing Professor Quirrell's death in his first year.",
"Based on the clues found in the Half-Blood Prince’s textbook, why did Snape likely invent the 'Sectumsempra' spell specifically for enemies?",
"Analyze the irony of Voldemort choosing Harry Potter as his 'equal' instead of Neville Longbottom, based on the specific wording of the prophecy.",
"How does the behavior of the Marauder’s Map toward Severus Snape reflect the personalities of its four original creators?",
"Reconstruct the timeline of the destruction of the seven Horcruxes, identifying which object was destroyed by whom and with what weapon.",
"Explain why the Sword of Gryffindor was able to destroy the locket Horcrux even though it was not originally forged for that purpose.",
"Compare Hermione’s logic in solving the potions riddle in the Chamber of Secrets with the logic required to enter the Ravenclaw Common Room.",
"If a wizard must 'intend' to cast an Unforgivable Curse for it to work, analyze Harry’s attempt to use Crucio on Bellatrix Lestrange in the Ministry.",
"Explain how the use of the Pensieve allows a wizard to see details in a memory that they did not consciously notice when the event originally occurred.",
"Contrast the motivations of Regulus Black and Severus Snape in their respective decisions to betray Lord Voldemort.",
"Describe the flaw in Voldemort’s logic when he decided to use Harry’s blood to rebuild his own body in the graveyard.",
"Analyze why Dumbledore allowed Snape to be the one to kill him, and how this protected Draco Malfoy’s soul according to their plan.",
"How did the presence of a Horcrux inside Harry influence his ability to speak Parseltongue and his mental connection to Voldemort?",
"Explain the relationship between the 'Tale of the Three Brothers' and the specific items Harry, Dumbledore, and Voldemort possessed at the end of the series.",
"Why was it logically necessary for Harry to 'die' in the Forbidden Forest for Voldemort to truly be defeated?",
"Analyze the shift in Kreacher the House-elf’s loyalty from the beginning of the fifth book to the middle of the seventh book.",
"How does the discovery of the 'R.A.B.' note in the locket change the protagonists' understanding of the difficulty of finding the remaining Horcruxes?",
"Explain the difference between a 'Portkey' and 'Apparition' in terms of the magical laws and restrictions mentioned across the books.",
]

async def run_hallucination_test():
    rag_service = RAGService()
    
    for q in TEST_QUESTIONS:
        logger.info(f"TESTING QUERY: {q}")
        
        docs = await rag_service.vector_service.query(q)
        answer = await rag_service.answer_question(q)
        
        logger.info(f"CONTEXT RETRIEVED: {[d.metadata['source'] for d in docs]}")
        logger.info(f"FINAL ANSWER: {answer}")
        logger.info("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_hallucination_test())