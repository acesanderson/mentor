from pathlib import Path
import json
from Kramer import Curation
import Levenshtein

dir_path = Path(__file__).resolve().parent
json_file = dir_path / "mentor_evaluation.json"

with open(json_file, "r") as file:
    data = json.load(file)

if __name__ == "__main__":
    curations = []
    for datum in data:
        json_obj, score = json.loads(datum[0]), datum[1]
        curation = Curation(**json_obj)
        curations.append((score, curation))
    # Sort curations by score
    # curations.sort(key=lambda x: x[0], reverse=False)
    # Print the top 5 curations
    title = "Business Analysis Foundations"
    levenshtein_distances = []
    for _, curation in curations:
        levenshtein_distances.append(
            (Levenshtein.distance(title, curation.title), curation)
        )
    # sort levenshtein_distances by first element in each tuple only
    levenshtein_distances.sort(key=lambda x: x[0])
    for d in levenshtein_distances[:10]:
        print(d[1])
