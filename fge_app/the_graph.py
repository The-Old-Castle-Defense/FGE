from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

class TheGraph:

    def __init__(self, rpc):
        self.transport = AIOHTTPTransport(url=rpc)
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)


    def query(self, _event, _filter):
        _q = """
            query {
              %s (orderBy: blockTimestamp, orderDirection: desc, first: 10) {
                %s
              }
            }
            """ % (_event, "\n".join(_filter))
        print(_q)
        query = gql(_q)
        response = self.client.execute(query)
        return response

    def custom_query(self, _q):
        try:
            query = gql(_q)
            response = self.client.execute(query)
            return response
        except Exception as exc:
            return {"data": {}}

