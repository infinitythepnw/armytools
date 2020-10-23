import json
import requests


# cflorka
# Oct 21, 2020
# NOTE: Army builder has bug so "Generate Army Code" string isn't
# working properly, so only string in saved lists under name in
# Server-saved games is currently working.
def getJSONfromArmyCode(armyCodeStr):
    '''
    Gets JSON from army builder based on army code passed as argument.

    Takes the CB api format, and reduces the data down to what one would
    find in the army builder.

    Parameters
    ----------
    armyCodeStr : string
        String obtained from army builder by clicking "Generate Army Code"
        button, or copying the string found under army when selecting a saved
        army which is saved on the server.

    Returns
    -------
    armyJSON : Dict/JSON Object
        JSON object returned when calling api with armyCodeStr
    '''
    url = "https://api.corvusbelli.com/army/lists/{}".format(armyCodeStr)
    getResponse = requests.get(url)
    armyJSON = getResponse.json()
    return armyJSON


def buildCustomTrooperObj(origTrooperObj):
    '''
    Returns trooper data from CB's format to more condensed format.

    Takes the JSON object in CB api format,
    and reduces the data down to what one would find in the army builder.

    Parameters
    ----------
    origTrooperObj : Dict/JSON Object
        CB's JSON object for a trooper, found as entry in "options" list.

    Returns
    -------
    newTrooperObj : Dict/JSON Object
        New JSON object with only relevant data found in army builder list.
    '''
    newTrooperObj = {}
    swc = float(origTrooperObj["swc"])
    pts = origTrooperObj["points"]
    equipment = origTrooperObj["equipName"]
    newTrooperObj["name"] = origTrooperObj["name"]
    if origTrooperObj["skillsName"] is not None:
        newTrooperObj["name"] += " ({})".format(origTrooperObj["skillsName"])
    newTrooperObj["weaponsAndEquipment"] = origTrooperObj["weaponsName"]
    if equipment is not None:
        newTrooperObj["weaponsAndEquipment"] += equipment
    newTrooperObj["ccWeapons"] = origTrooperObj["weaponsCCName"]
    newTrooperObj["swc"] = swc
    newTrooperObj["points"] = pts
    return newTrooperObj


def getGroupOrders(targetGroupId, armyListJSON):
    '''
    Returns group order data from CB's format to more flattened format.

    Parameters
    ----------
    targetGroupId : string
        The ID used to pull correct group's order data from CB's JSON

    Returns
    -------
    orders : Dict/JSON Object
        New JSON object with flatter structure.
    '''
    orders = {}
    for group in armyListJSON["verify"]["groups"]:
        if group["id"] == targetGroupId:
            for orderTypeData in group["orders"]:
                orders[orderTypeData["type"]] = orderTypeData["total"]
            break
    return orders


def getArmyDataFromCode(armyCodeStr):
    '''
    Takes an Army Code String and returns JSON data of army list.

    JSON returned is pared down and flattened to make easier for
    formatting.

    Parameters
    ----------
    armyCodeStr : string
        String obtained from army builder by clicking "Generate Army Code"
        button, or copying the string found under army when selecting a saved
        army which is saved on the server.

    Returns
    -------
    armyJSON : Dict/JSON Object
        JSON object with army list data.
    '''
    armyGroupList = []

    armyListFullJSON = getJSONfromArmyCode(armyCodeStr)
    for group in armyListFullJSON["groups"]:
        groupNum = group["id"]
        groupUnitList = []
        groupSwcTotal = 0.0
        groupPtsTotal = 0
        for trooper in group["options"]:
            if len(trooper["includes"]) > 0:
                for subtrooper in trooper["includes"]:
                    trooperData = buildCustomTrooperObj(subtrooper)
                    groupSwcTotal += trooperData["swc"]
                    groupPtsTotal += trooperData["points"]
                    groupUnitList.append(trooperData)
            else:
                trooperData = buildCustomTrooperObj(trooper)
                groupSwcTotal += trooperData["swc"]
                groupPtsTotal += trooperData["points"]
                groupUnitList.append(trooperData)
        # Build group Object
        groupObject = {}
        groupObject["name"] = "Group {}".format(groupNum)
        groupObject["swc"] = groupSwcTotal
        groupObject["points"] = groupPtsTotal
        groupObject["orders"] = getGroupOrders(groupNum, armyListFullJSON)
        groupObject["units"] = groupUnitList
        armyGroupList.append(groupObject)
    # Build Army Object
    armyObject = {}
    armyObject["name"] = armyListFullJSON["name"]
    armyObject["faction"] = armyListFullJSON["factionSlug"]
    armyObject["maxSwc"] = armyListFullJSON["verify"]["swc"]["max"]
    armyObject["swc"] = armyListFullJSON["verify"]["swc"]["total"]
    armyObject["maxPts"] = armyListFullJSON["verify"]["points"]["max"]
    armyObject["points"] = armyListFullJSON["verify"]["points"]["total"]
    armyObject["Groups"] = armyGroupList
    armyJSON = json.dumps(armyObject, indent=2)
    return armyJSON

# Test code below
# with open("testOutput.json", "w") as write_file:
    # outputString1 = getArmyDataFromCode("g6wpsm4Seh")
    # outputString2 = getArmyDataFromCode("Uj8CvHOBuh")
    # write_file.write(outputString1)
