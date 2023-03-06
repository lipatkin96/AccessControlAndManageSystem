import sys
import sqlite3
import datetime


class WorkerData:
    def __init__(self, key: int, name: str, places: list):
        self.key = key
        self.name = name
        self.places = places


class AccessController:
    def __init__(self):
        self.connection = sqlite3.connect("AccessWorkerDB.db")
        self.checkAccessRequest = """
            SELECT * 
            FROM ACCESS_PLACES 
            WHERE card_key = {} AND place_id = {}"""
        self.addNewWorkerCardRequest = """
            INSERT INTO WORKER_CARDS 
            (key, worker_name) 
            VALUES('{}', '{}')"""
        self.addCardAccessRequest = """
            INSERT INTO ACCESS_PLACES 
            (card_key, place_id) 
            VALUES('{}', '{}')"""
        self.getWorkerListRequest = """
            SELECT * 
            FROM WORKER_CARDS"""
        self.getWorkerAccessPlacesRequest = """
            SELECT place_id
            FROM ACCESS_PLACES
            WHERE card_key = {} """
        # self.getWorkerAccessPlacesListRequest = """
        #     SELECT WORKER_CARDS.key, WORKER_CARDS.worker_name,
        #            ACCESS_PLACES.place_id
        #     FROM WORKER_CARDS
        #     INNER JOIN ACCESS_PLACES
        #     ON WORKER_CARDS.key = ACCESS_PLACES.card_key"""
        self.getHistoryRequest = """
            SELECT WORKER_CARDS.worker_name, place_id, time
            FROM HISTORY
            INNER JOIN WORKER_CARDS
            ON HISTORY.card_key = WORKER_CARDS.key"""
        self.addNewAccessToPlace = """
            INSERT INTO HISTORY 
            (card_key, place_id, time) 
            VALUES(?, ?, ?)"""

    def hasAccess(self,
                  cardKey: int,
                  placeId: int) -> bool:
        result = self.connection.cursor().execute(
            self.checkAccessRequest.format(cardKey, placeId)
        ).fetchone()
        if result is None:
            return False
        return True

    def addNewWorkerCard(self,
                         cardKey: int,
                         workerName: str,
                         placeId: int):
        cursor = self.connection.cursor()
        cursor.execute(
            self.addNewWorkerCardRequest.format(cardKey, workerName)
        )
        cursor.execute(
            self.addCardAccessRequest.format(cardKey, placeId)
        )
        self.connection.commit()

    def tryToGetAccess(self,
                       cardKey: int,
                       placeId: int) -> bool:
        cursor = self.connection.cursor()
        if self.hasAccess(cardKey, placeId):
            cursor.execute(self.addNewAccessToPlace, (cardKey, placeId, datetime.datetime.now()))
            self.connection.commit()
            return True
        return False

    def getWorkerList(self) -> list:
        cursor = self.connection.cursor()
        cursor.execute(self.getWorkerListRequest)

        kek = []
        workers = cursor.fetchall()
        for workerRow in workers:
            cardKey = int(workerRow[0])
            results = cursor.execute(
                self.getWorkerAccessPlacesRequest.format(cardKey)).fetchall()
            placesList = []
            for placeTuple in results:
                placesList.append(placeTuple[0])
            kek.append(WorkerData(cardKey, workerRow[1], placesList))

        return kek

    def getHistory(self) -> list:
        cursor = self.connection.cursor()
        cursor.execute(self.getHistoryRequest)
        return cursor.fetchall()