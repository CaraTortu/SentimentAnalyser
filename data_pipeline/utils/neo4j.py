from dataclasses import dataclass
import neo4j
import os
from dotenv import load_dotenv

load_dotenv()

neo4j_url = os.getenv("NEO4J_URL")
neo4j_username = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

SEARCH_QUERY = """
MATCH (p:Project {datasetName: "enron2"}), 
      (p)-[:OWNS]-(u:User {email: "exampleC@enron.com"}), 
      (u)-[r:SENTIMENT]-(u2:User)
RETURN u, r, u2
"""

INSERT_SENTIMENT_QUERY = """
MERGE (p:Project {datasetName: $datasetName})
MERGE (sender:User {email: $senderEmail})
MERGE (receiver:User {email: $receiverEmail})
MERGE (sender)-[r:SENTIMENT]-(receiver)
MERGE (p)-[:OWNS]->(sender)
MERGE (p)-[:OWNS]->(receiver)
ON CREATE SET r.sentiment = $sentiment, r.emailsSent = $emailsSent
ON MATCH SET r.sentiment = $sentiment, r.emailsSent = $emailsSent
RETURN sender, receiver, r
"""


def get_driver() -> neo4j.Driver:
    driver = neo4j.GraphDatabase.driver(
        neo4j_url, auth=(neo4j_username, neo4j_password)  # pyright: ignore
    )

    return driver


@dataclass
class SentimentUser:
    email: str


def add_users(
    driver: neo4j.Driver,
    datasetName: str,
    sender: SentimentUser,
    receiver: SentimentUser,
    sentimentScore: float,
    emailsSent: int,
) -> neo4j.EagerResult:
    result = driver.execute_query(
        INSERT_SENTIMENT_QUERY,
        datasetName=datasetName,
        senderEmail=sender.email,
        receiverEmail=receiver.email,
        sentiment=sentimentScore,
        emailsSent=emailsSent,
    )

    return result
