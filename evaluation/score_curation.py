"""
all-MiniLM-L6-v2 is a lightweight model that does NOT use prompting.
Later, try the bge family of models (fex. BAAI/bge-small-en-v1.5) then pass prompt_name in the .encode function.
"""

from Kramer import Curation
from sentence_transformers import SentenceTransformer
from Kramer.certs.CertsCRUD import get_all_cert_titles, get_cert_by_name
from torch import Tensor
from Mentor import Mentor
from statistics import mean
import json
from pathlib import Path
from rich.console import Console

embedding_model = SentenceTransformer("all-MiniLM-L6-v2", trust_remote_code=True).cuda()
dir_path = Path(__file__).resolve(strict=True).parent
json_file = dir_path / "mentor_evaluation.json"
console = Console(width=100)


def get_certs() -> list[Curation]:
    """
    Get all certificates from the database.
    :return: A list of all certificates.
    """
    cert_titles = get_all_cert_titles()
    certs = []
    for cert_title in cert_titles:
        cert = get_cert_by_name(cert_title)
        try:
            certs.append(cert)
        except Exception as e:
            print(f"Error retrieving cert {cert_title}: {e}")
    return certs


def generate_cert_embedding(cert: Curation) -> Tensor:
    """
    Generate an embedding for a given certificate (or the curation we are evaluating).
    :param cert: The certificate to generate an embedding for.
    :return: The embedding of the certificate.
    """
    doc = cert.snapshot
    cert_embedding = embedding_model.encode(doc)
    return cert_embedding


def generate_cert_embeddings(certs: list[Curation]) -> list[Tensor]:
    """
    Generate embeddings for a list of certificates.
    :param certs: The list of certificates to generate embeddings for.
    :return: A list of embeddings for the certificates.
    """
    return [generate_cert_embedding(cert) for cert in certs]


def get_similarities(
    curation_embedding: Tensor, cert_embeddings: list[Tensor]
) -> list[float]:
    """
    Get the similarities between a curation embedding and a list of certificate embeddings.
    :param curation_embedding: The embedding of the curation we are evaluating.
    :param cert_embeddings: The list of embeddings for the certificates.
    :return: A list of similarities between the curation and the certificates.
    """
    similarities = []
    for cert_embedding in cert_embeddings:
        similarity = embedding_model.similarity(curation_embedding, cert_embedding)
        similarities.append(similarity)
    return similarities


def generate_score(curation: Curation, certs: list[Curation], n: int = 10) -> float:
    """
    Generate a score for a given curation based on its similarity to a list of certificates.
    :param curation: The curation we are evaluating.
    :param certs: The list of certificates to compare against.
    :return: A tuple containing the embedding of the curation and a list of similarities.
    """
    cert_embeddings = generate_cert_embeddings(certs)
    curation_embedding = generate_cert_embedding(curation)
    similarities = get_similarities(curation_embedding, cert_embeddings)
    scalar_similarities = [float(sim.item()) for sim in similarities]
    sorted_similarities = sorted(scalar_similarities, reverse=True)
    top_similarities = sorted_similarities[:n]
    score = mean(top_similarities)
    return score


def mentor_evaluation_chain(
    topic: str, certs: list[Curation]
) -> tuple[Curation, float]:
    """
    Generate a mentor curation, then generate a score.
    """
    curation = Mentor(topic, cache=False)
    score = generate_score(curation, certs)
    return curation, score


if __name__ == "__main__":
    certs = get_certs()
    test_topic = "Business Analysis Fundamentals"
    test_results = []
    n_iterations = 100
    for i in range(n_iterations):
        console.print(f"[green]Evaluating {i+1}/{n_iterations}...[/green]")
        try:
            curation, score = mentor_evaluation_chain(test_topic, certs)
            console.print("[yellow]----------------------------[/yellow]")
            console.print("[cyan]" + curation + "[/cyan]")
            console.print("[yellow]----------------------------[/yellow]")
            curation = curation.model_dump_json()
            test_results.append((curation, score))
        except Exception as e:
            print(f"Error during evaluation: {e}")
            continue
        finally:
            with open(json_file, "w") as f:
                json.dump(test_results, f, indent=4)
