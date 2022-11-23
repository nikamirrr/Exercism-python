import json


class RestAPI:
    def __init__(self, database=None):
        self.database = database or dict()
        self.database["users_by_name"] = {user_object["name"]: user_object
                                          for user_object in self.database["users"]}

    def get(self, url, payload=None):
        if url and url[0] == "/":
            url = url[1:]
            if url == "users":
                if not payload:
                    return json.dumps({"users": sorted(self.database["users"], key=(lambda x: x["name"]))})
                else:
                    payload = json.loads(payload)
                    if "users" in payload:
                        return json.dumps({"users": sorted((self.database["users_by_name"][name]
                                                            for name in payload["users"]),
                                                           key=(lambda x: x["name"]))})

    def post(self, url, payload=None):
        if url and url[0] == "/":
            url = url[1:]
            if url == "add":
                if payload:
                    payload = json.loads(payload)
                    user_object = {"name": payload["user"],
                                   "owes": {},
                                   "owed_by": {},
                                   "balance": 0}
                    if user_object["name"] not in self.database["users_by_name"]:
                        self.database["users"].append(user_object)
                    self.database["users_by_name"][user_object["name"]] = user_object
                    return json.dumps(user_object)
            elif url == "iou":
                if payload:
                    payload = json.loads(payload)
                    lo = self.database["users_by_name"][payload["lender"]]
                    bo = self.database["users_by_name"][payload["borrower"]]
                    a = payload["amount"]
                    if payload["lender"] in bo["owes"]:
                        bo["owes"][payload["lender"]] += a
                    else:
                        bo["owes"][payload["lender"]] = a
                    bo["balance"] -= a
                    if payload["borrower"] in lo["owed_by"]:
                        lo["owed_by"][payload["borrower"]] += a
                    else:
                        lo["owed_by"][payload["borrower"]] = a
                    lo["balance"] += a

                    if payload["borrower"] in lo["owes"]:
                        diff = lo["owed_by"][payload["borrower"]] - lo["owes"][payload["borrower"]]
                        if diff <= 0:
                            del lo["owed_by"][payload["borrower"]]
                            del bo["owes"][payload["lender"]]
                            del lo["owes"][payload["borrower"]]
                            del bo["owed_by"][payload["lender"]]
                            if diff < 0:
                                diff = -diff
                                lo["owes"][payload["borrower"]] = diff
                                bo["owed_by"][payload["lender"]] = diff
                        else:
                            del lo["owes"][payload["borrower"]]
                            del bo["owed_by"][payload["lender"]]
                            lo["owed_by"][payload["borrower"]] = diff
                            bo["owes"][payload["lender"]] = diff






                    return json.dumps({"users": sorted((self.database["users_by_name"][name]
                                                       for name in (payload["lender"],
                                                                    payload["borrower"])),
                                                       key=(lambda x: x["name"]))})
