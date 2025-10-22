from siphonserver.client.siphonclient import (
    SiphonClient,
    CuratorRequest,
    CuratorResponse,
)


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
    client = SiphonClient()
    response: CuratorResponse = client.curate(request)
    results = response.results
    results_tuples = [(result.id, result.score) for result in results]
    return results_tuples
