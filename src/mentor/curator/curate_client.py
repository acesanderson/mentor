from headwater_client.client.headwater_client import HeadwaterClient
from headwater_api.classes import CuratorRequest, CuratorResponse


def query_server(
    query_string: str,
    k: int = 5,
    n_results: int = 50,
    model_name: str = "bge",
    cached=True,
) -> list[tuple]:
    request = CuratorRequest(
        query_string=query_string,
        k=k,
        n_results=n_results,
        model_name=model_name,
        cached=cached,
    )
    client = HeadwaterClient()
    response: CuratorResponse = client.curator.curate(request)
    results = response.results
    results_tuples = [(result.id, result.score) for result in results]
    return results_tuples
