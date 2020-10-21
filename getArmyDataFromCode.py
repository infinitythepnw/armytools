import json
import requests


def getJSONfromArmyCode(armyCodeStr):
    url = "https://api.corvusbelli.com/army/lists/{}".format(armyCodeStr)
    getResponse = requests.get(url)
    armyJSON = getResponse.json()
    return armyJSON


def addTrooperToGroup(trooperObj, unitList):
    unitDict = {}
    swc = float(trooperObj["swc"])
    pts = trooperObj["points"]
    equipment = trooperObj["equipName"]
    unitDict["name"] = trooperObj["name"]
    if trooperObj["skillsName"] is not None:
        unitDict["name"] += " ({})".format(trooperObj["skillsName"])
    unitDict["weaponsAndEquipment"] = trooperObj["weaponsName"]
    if equipment is not None:
        unitDict["weaponsAndEquipment"] += equipment
    unitDict["ccWeapons"] = trooperObj["weaponsCCName"]
    unitDict["swc"] = swc
    unitDict["points"] = pts

    unitList.append(unitDict)
    return (swc, pts)


def getGroupOrders(targetGroupNumber, armyListJSON):
    orders = {}
    for group in armyListJSON["verify"]["groups"]:
        if group["id"] == targetGroupNumber:
            for orderTypeData in group["orders"]:
                orders[orderTypeData["type"]] = orderTypeData["total"]
            break
    return orders


def getArmyDataFromCode(armyCodeStr):
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
                    (swc, pts) = addTrooperToGroup(subtrooper, groupUnitList)
                    groupSwcTotal += swc
                    groupPtsTotal += pts
            else:
                (swc, pts) = addTrooperToGroup(trooper, groupUnitList)
                groupSwcTotal += swc
                groupPtsTotal += pts
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
    # write_file.write(outputString2)
