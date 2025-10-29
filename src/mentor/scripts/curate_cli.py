import argparse
from rich.console import Console
from mentor.curator.curate_client import query_server

console = Console()


def main():
    # Our arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("query_string", nargs="?", help="A query for the text.")
    parser.add_argument(
        "-k",
        "--number_responses",
        type=int,
        default=5,
        help="Original pool size: this is 5 by default.",
    )
    parser.add_argument(
        "-n",
        "--original_batch_size",
        type=int,
        default=50,
        help="Number of responses: this is 50 by default.",
    )
    parser.add_argument(
        "-m",
        "--model_name",
        type=str,
        default="mxbai",
        help="Model name to use for embeddings: this is 'bge' by default.",
    )
    parser.add_argument(
        "-c",
        "--no_cache",
        action="store_true",
        default=False,
        help="Disable caching for this query.",
    )
    args = parser.parse_args()
    query_string = args.query_string
    if not query_string:
        console.print("[red]Error: You must provide a query string.[/red]")
        return
    if args.number_responses:
        k = args.number_responses
    else:
        k = 5
    if args.original_batch_size:
        n = args.original_batch_size
    else:
        n = 50
    results = query_server(
        query_string,
        k=k,
        n_results=n,
        model_name=args.model_name,
        cached=not args.no_cache,
    )
    console.print(f"[green]Query: {query_string}[/green]")
    console.print(
        "[yellow]------------------------------------------------------------------------[/yellow]"
    )
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
