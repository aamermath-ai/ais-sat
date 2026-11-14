# SAT AIS - Reading & Writing batch 3B: 30 original SAT-Hard items (Expression of Ideas; Standard English Conventions).
# The correct choice is listed first; the app shuffles choices. Run: python3 source/rw_batch3b.py
import json, os
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bank")
SRC = "SAT AIS original item, written to the College Board Digital SAT content specifications"
EI, SE = "Expression of Ideas", "Standard English Conventions"
RS, TR, BO, FS = "Rhetorical Synthesis", "Transitions", "Boundaries", "Form, Structure, and Sense"
Q = []
def mc(id, dom, skill, passage, stem, choices, steps, key):
    Q.append((id, dict(section="rw", domain=dom, skill=skill, difficulty=3, type="mc", passage=passage, stem=stem,
                       choices=choices, answer=0, steps=steps, key=key, source=SRC)))
NOTES = "While researching a topic, a student has taken the following notes:\n"
def rsq(goal): return "The student wants to " + goal + ". Which choice most effectively uses relevant information from the notes to accomplish this goal?"
TRQ = "Which choice completes the text with the most logical transition?"
CONV = "Which choice completes the text so that it conforms to the conventions of Standard English?"

# ---------------- Rhetorical Synthesis (6)
mc("rw-ei-33", EI, RS,
 NOTES + "• The Svalbard Global Seed Vault is located on a Norwegian island in the Arctic.\n• It stores duplicate seed samples from gene banks around the world.\n• In 2015, researchers withdrew seeds to rebuild a collection in Syria damaged by war.\n• The permafrost around the vault helps keep the seeds frozen even if power fails.",
 rsq("explain how the vault served its purpose in a specific case"),
 ["When war damaged a gene bank in Syria, researchers withdrew duplicate seeds from the Svalbard vault in 2015 to rebuild the collection.",
  "The Svalbard Global Seed Vault, on a Norwegian island in the Arctic, stores duplicate seed samples from gene banks around the world.",
  "The permafrost surrounding the Svalbard vault helps keep its stored seeds frozen even if the vault's power supply fails.",
  "Gene banks around the world, including one in Syria, send duplicate seed samples to a vault on a Norwegian Arctic island."],
 ["The goal has two parts: the vault's purpose (backing up gene banks) and a specific case.",
  "Only the Syria withdrawal shows the backup being used.",
  "The other choices describe the vault, its permafrost or its deposits without showing it serving its purpose in a case."],
 "Check each part of the goal: here, both “purpose” and “specific case.”")
mc("rw-ei-34", EI, RS,
 NOTES + "• Mangrove forests grow along tropical coastlines.\n• Their dense roots slow waves and trap sediment.\n• A 2020 study estimated that mangroves prevent more than $65 billion in flood damage each year.\n• About 35% of the world's mangroves were lost between 1980 and 2000.",
 rsq("emphasize the economic value of protecting mangroves to an audience of government officials"),
 ["Mangroves prevent an estimated $65 billion in flood damage each year, a reason to protect forests that lost about 35% of their area between 1980 and 2000.",
  "Mangrove forests, which grow along tropical coastlines around the world, have dense roots that slow incoming waves and trap sediment near the shore.",
  "About 35% of the world's mangrove forests were lost between 1980 and 2000, according to estimates.",
  "Because their roots slow waves and trap sediment, mangrove forests can grow along tropical coastlines."],
 ["The goal: economic value plus protection.",
  "Only the first choice uses the $65 billion figure and ties it to protecting forests that are being lost.",
  "The others give biology, the loss alone or a reversed cause-and-effect."],
 "For a persuasive goal, pick the choice that uses the most relevant figure for that audience.")
mc("rw-ei-35", EI, RS,
 NOTES + "• Ada Lovelace (1815–1852) worked with Charles Babbage on his proposed Analytical Engine.\n• Babbage designed the machine, but it was never built.\n• Lovelace published a method for the engine to calculate Bernoulli numbers.\n• She also suggested such a machine could compose music if given the right rules.",
 rsq("present Lovelace as someone who saw possibilities beyond calculation"),
 ["Lovelace suggested that a machine like the Analytical Engine could compose music if given the right rules, a use far beyond arithmetic.",
  "Lovelace published a method for the Analytical Engine to calculate Bernoulli numbers.",
  "Lovelace worked closely with Charles Babbage on his proposed Analytical Engine, a calculating machine that he designed but that was never built.",
  "Babbage designed the Analytical Engine, and Lovelace published work related to the machine."],
 ["“Beyond calculation” points to the music idea.",
  "Calculating Bernoulli numbers is calculation, the opposite of the goal.",
  "The remaining choices give background, not her vision."],
 "Distractors often use true notes that miss the goal's key word.")
mc("rw-ei-36", EI, RS,
 NOTES + "• Study A tested a reading app with 400 second-graders for one school year.\n• Students using the app gained 8 points on a reading test.\n• Students in a comparison group gained 7 points.\n• The difference was not statistically significant.",
 rsq("present the study's results accurately to readers who might assume the app was highly effective"),
 ["Although app users gained 8 points and the comparison group 7, the difference was not statistically significant.",
  "Students using the reading app gained 8 points on a reading test over a school year.",
  "A study tested a reading app with 400 second-graders for an entire school year.",
  "The reading app helped the 400 second-graders who used it gain more points on a reading test than students in the comparison group."],
 ["Accuracy for skeptical-of-effect readers requires the comparison and the lack of significance.",
  "Only the first choice gives both groups' gains and the key caveat.",
  "The second and fourth suggest an effect without the caveat; the third gives no results."],
 "“Accurately” usually means including the qualification that limits a result.")
mc("rw-ei-37", EI, RS,
 NOTES + "• The axolotl is a salamander native to lakes near Mexico City.\n• It can regrow lost limbs, parts of its heart, and even parts of its brain.\n• Scientists study it to understand tissue regeneration.\n• Wild populations have declined sharply because of pollution and habitat loss.",
 rsq("contrast the axolotl's value to science with its situation in the wild"),
 ["Though scientists prize the axolotl for its ability to regrow limbs and organs, its wild populations have declined sharply.",
  "The axolotl, a salamander native to lakes near Mexico City, can regrow lost limbs and parts of its heart.",
  "Scientists study the axolotl, which can regrow parts of its brain, to understand tissue regeneration.",
  "Pollution and habitat loss have caused the wild populations of the axolotl, a salamander native to lakes near Mexico City, to decline sharply."],
 ["A contrast needs both sides: scientific value and decline in the wild.",
  "Only the first choice joins them with “though.”",
  "The others give only one side."],
 "Contrast goals need two ideas linked by a contrast word.")
mc("rw-ei-38", EI, RS,
 NOTES + "• The Voyager 1 probe was launched in 1977.\n• In 2012, it became the first human-made object to enter interstellar space.\n• It carries a golden record with sounds and images from Earth.\n• Its signals now take more than 22 hours to reach Earth.",
 rsq("emphasize how far Voyager 1 has traveled"),
 ["Voyager 1, the first human-made object to enter interstellar space, is now so distant that its signals take over 22 hours to reach Earth.",
  "Launched in 1977, Voyager 1 carries a golden record of sounds and images from Earth.",
  "Voyager 1 was launched in 1977 and carries a golden record with sounds from Earth.",
  "In 2012, the Voyager 1 probe, launched in 1977 and carrying a golden record of sounds and images from Earth, made history in space exploration."],
 ["Distance is shown by entering interstellar space and the 22-hour signal delay.",
  "The first choice uses both.",
  "The others mention launch date, the record or vague “history” without conveying distance."],
 "Pick the notes that measure the goal's quality, here distance.")

# ---------------- Transitions (6)
mc("rw-ei-39", EI, TR,
 "Early naturalists assumed that cuckoo chicks, which are raised by birds of other species, simply benefit at their hosts' expense. Recent work on crows in Spain complicates that view. Crow nests containing a cuckoo chick were more likely to survive attacks by predators, because the chick releases a foul-smelling substance when disturbed. ______ in years with many predators, hosting a cuckoo may actually help the crows.",
 TRQ, ["Thus,", "Nevertheless,", "Similarly,", "For instance,"],
 ["The sentence before gives a benefit: nests with cuckoos survived predators more often.",
  "The blank sentence draws the conclusion from that: hosting a cuckoo may help.",
  "That is a result, so “Thus.”",
  "“Nevertheless” signals contrast, “Similarly” a parallel, and “For instance” an example."],
 "A conclusion drawn from the previous sentence takes a cause-and-effect transition.")
mc("rw-ei-40", EI, TR,
 "Most early photographs required exposures of several minutes, so busy city streets often appeared empty: moving people and carriages left no trace. ______ a man in an 1838 image of a Paris boulevard by Louis Daguerre does appear, because he stood still long enough while having his boots shined.",
 TRQ, ["Notably,", "Consequently,", "Likewise,", "In other words,"],
 ["Streets usually appeared empty, but this man does appear: an exception worth pointing out.",
  "“Notably” introduces a remarkable exception.",
  "“Consequently” would make him a result of empty streets; “Likewise” means similarity; “In other words” restates."],
 "Ask how the new sentence relates: exception, result, similarity or restatement.")
mc("rw-ei-41", EI, TR,
 "The Inca empire had no system of writing as Europeans understood it. ______ it kept detailed records of censuses, taxes, and labor obligations using khipus, arrangements of knotted cords whose colors, positions, and knot types encoded numbers and possibly other information.",
 TRQ, ["Even so,", "Therefore,", "In addition,", "As a result,"],
 ["No writing, yet detailed records: a contrast with what you'd expect.",
  "“Even so” signals that contrast.",
  "“Therefore” and “As a result” imply records because of no writing; “In addition” adds a similar point."],
 "Expectation followed by its opposite calls for a concession transition.")
mc("rw-ei-42", EI, TR,
 "Researchers testing a new malaria vaccine first gave it to a small group of adults to check its safety. Once no serious side effects appeared, they expanded the trial to several hundred volunteers to determine the best dose. ______ they launched a study with thousands of children across four countries to measure how well the vaccine prevented disease.",
 TRQ, ["Finally,", "Instead,", "Meanwhile,", "Conversely,"],
 ["The text lists stages in order: safety, dose, then a large effectiveness study.",
  "The last stage takes “Finally.”",
  "“Instead” means replacing, “Meanwhile” means at the same time, and “Conversely” means the opposite."],
 "Sequences of stages call for time-order transitions.")
mc("rw-ei-43", EI, TR,
 "Planting trees is often promoted as a simple way to remove carbon dioxide from the air. In some dry grasslands, however, dense tree planting can reduce groundwater and increase the risk of fire. ______ ecologists argue that restoration projects should match vegetation to local conditions rather than plant trees everywhere.",
 TRQ, ["For this reason,", "By contrast,", "Previously,", "Similarly,"],
 ["Problems with tree planting in some places lead ecologists to argue for local matching.",
  "The argument follows from the problems: “For this reason.”",
  "“By contrast” and “Similarly” set up comparisons, and “Previously” is about time."],
 "If the sentence is a recommendation based on what came before, use a cause-and-effect transition.")
mc("rw-ei-44", EI, TR,
 "Jazz musician Mary Lou Williams is often remembered for her work as a pianist with big bands in the 1930s. ______ her influence extended well beyond performance: she mentored younger musicians such as Thelonious Monk and Dizzy Gillespie, who often gathered at her Harlem apartment to share new ideas.",
 TRQ, ["Yet", "Thus,", "Likewise,", "For instance,"],
 ["Sentence 1: she is remembered mainly as a pianist. Sentence 2: her influence went well beyond that.",
  "The second sentence pushes against the limited picture in the first, so it needs a contrast: \u201cYet.\u201d",
  "\u201cThus\u201d makes it a result, \u201cLikewise\u201d a similarity, and \u201cFor instance\u201d an example of being a pianist."],
 "If the second sentence corrects or expands a narrow view, use a contrast transition.")

# ---------------- Boundaries (6)
mc("rw-se-39", SE, BO,
 "The biologist Ynes Mexia did not begin collecting plants until she was fifty-five ______ over the next thirteen years, she gathered some 150,000 specimens across Mexico and South America, including about 500 species new to science.",
 CONV, ["years old;", "years old,", "years old", "years, old;"],
 ["Both sides are complete sentences: “Mexia did not begin…fifty-five years old” and “over the next thirteen years, she gathered…”",
  "Two independent clauses need a semicolon (or a period).",
  "A comma alone makes a comma splice, nothing makes a run-on, and the comma inside “years, old” breaks a phrase."],
 "Test whether both sides could stand alone; if so, use a semicolon.")
mc("rw-se-40", SE, BO,
 "Arriving in the capital after months at sea, the expedition's members found that their findings had already been ______ a rival team had announced the discovery of the same strait two weeks earlier.",
 CONV, ["anticipated:", "anticipated,", "anticipated", "anticipated, and,"],
 ["The second clause explains what “anticipated” means here.",
  "A colon introduces an explanation after a complete clause.",
  "A comma alone splices two clauses; no punctuation runs them together; “, and,” adds a stray comma."],
 "A colon can join two complete clauses when the second explains the first.")
mc("rw-se-41", SE, BO,
 "The painter Jacob Lawrence completed his Migration Series, sixty panels depicting the movement of African Americans from the rural South to northern ______ when he was just twenty-three years old.",
 CONV, ["cities,", "cities;", "cities", "cities:"],
 ["“sixty panels depicting…cities” is an appositive opened by a comma after “Migration Series.”",
  "It must close with a matching comma.",
  "A semicolon or colon would cut the sentence wrongly, and no comma leaves the appositive unclosed."],
 "Nonessential phrases opened with a comma must close with a comma.")
mc("rw-se-42", SE, BO,
 "In her study of urban birds, ecologist Lena Haas recorded three kinds of song changes in noisy ______ higher pitch, longer notes, and singing at times when traffic was lighter.",
 CONV, ["areas:", "areas;", "areas, such as:", "areas, these were:"],
 ["The sentence before the blank is complete and announces “three kinds,” followed by the list.",
  "A colon introduces a list after a complete clause.",
  "A semicolon needs a full clause after it; “such as:” puts a colon after an incomplete phrase; “these were:” creates a comma splice."],
 "Use a colon after a complete clause that announces a list.")
mc("rw-se-43", SE, BO,
 "Scientists have found that octopuses can recognize individual ______ in one study, an octopus repeatedly squirted water at one particular researcher who had poked it, while ignoring others.",
 CONV, ["humans. In", "humans, in", "humans in", "humans, and in,"],
 ["Both parts are complete sentences.",
  "A period correctly separates them.",
  "A comma alone creates a comma splice, no punctuation creates a run-on, and “, and in,” adds an incorrect comma after “in.”"],
 "Two complete sentences need a period, semicolon or comma plus a conjunction.")
mc("rw-se-44", SE, BO,
 "The 2004 Indian Ocean tsunami led many nations to invest in warning systems that combine seafloor pressure ______ and computer models to estimate a wave's arrival time within minutes.",
 CONV, ["sensors, coastal tide gauges,", "sensors; coastal tide gauges;", "sensors: coastal tide gauges,", "sensors coastal tide gauges,"],
 ["The blank lists three items: seafloor pressure sensors, coastal tide gauges and computer models.",
  "Items in a simple list are separated by commas.",
  "Semicolons are for lists whose items contain commas; a colon would wrongly introduce the second item; missing commas merge two items."],
 "In a simple series, use commas between items.")

# ---------------- Form, Structure, and Sense (6)
mc("rw-se-45", SE, FS,
 "The collection of letters exchanged between the two scientists, now held at a university archive in Leiden, ______ how their friendship survived decades of professional rivalry.",
 CONV, ["reveals", "reveal", "have revealed", "are revealing"],
 ["The subject is “The collection” (singular), not “letters” or “scientists.”",
  "Singular subject, singular verb: “reveals.”",
  "The other choices are plural verbs that agree with the nearer nouns by mistake."],
 "Skip phrases between subject and verb to find the true subject.")
mc("rw-se-46", SE, FS,
 "Neither the engineers who designed the bridge nor the inspector who approved its plans ______ the effect that strong crosswinds would have on the deck.",
 CONV, ["was able to predict", "were able to predict", "have been able to predict", "are able to predict"],
 ["With “neither…nor,” the verb agrees with the nearer subject: “the inspector” (singular).",
  "The past context needs “was able.”",
  "“Were,” “have been” and “are” are plural or wrongly timed."],
 "With neither/nor and either/or, match the verb to the closer subject.")
mc("rw-se-47", SE, FS,
 "When the archaeologists finally opened the sealed chamber in 1922, they discovered that the ancient builders ______ the walls with a mixture of lime and crushed shells to keep out moisture.",
 CONV, ["had lined", "will line", "are lining", "line"],
 ["The discovery happened in 1922; the lining happened earlier still.",
  "An action before another past action takes the past perfect: “had lined.”",
  "Future, present progressive and simple present don't fit the timeline."],
 "Earlier-past actions take “had” + past participle.")
mc("rw-se-48", SE, FS,
 "Having studied hundreds of hours of recordings of humpback whales, ______",
 CONV,
 ["researchers concluded that the songs change gradually as new phrases spread from one population to another.",
  "the songs were found by the researchers to change gradually as new phrases spread from one population to another.",
  "it was concluded by researchers that the songs change gradually between populations.",
  "the conclusion of researchers was that the songs change gradually between populations."],
 ["The opening phrase must describe whoever did the studying: the researchers.",
  "So “researchers” must come right after the comma.",
  "The other choices make “the songs,” “it” or “the conclusion” the ones who studied, which are dangling modifiers."],
 "An opening modifier must be followed immediately by the noun it describes.")
mc("rw-se-49", SE, FS,
 "Each of the city's public libraries now lends out tools, musical instruments, and even fishing rods, and the program's organizers hope that ______ popularity will encourage other cities to adopt the idea.",
 CONV, ["its", "their", "it's", "they're"],
 ["The pronoun refers to “the program” (singular), and possession is needed.",
  "Singular possessive: “its.”",
  "“Their” is plural; “it's” means “it is”; “they're” means “they are.”"],
 "Find what the pronoun refers to, then check number and possession.")
mc("rw-se-50", SE, FS,
 "The museum's newest exhibit features dozens of maps drawn by sailors in the Pacific Islands, whose charts made of sticks and shells ______ ocean swells rather than coastlines, an approach that allowed navigators to cross thousands of miles of open water.",
 CONV, ["represented", "representing", "to represent", "having represented"],
 ["The clause “whose charts…______ ocean swells” needs a main verb for “charts.”",
  "Only “represented” is a finite verb.",
  "“Representing,” “to represent” and “having represented” can't serve as the clause's verb."],
 "Every clause needs a finite verb; -ing forms and infinitives alone can't do the job.")

if __name__ == "__main__":
    for id, q in Q:
        json.dump(q, open(os.path.join(B, id + ".json"), "w"), ensure_ascii=False)
    print(len(Q), "items written")
