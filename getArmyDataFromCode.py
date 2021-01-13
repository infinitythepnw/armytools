import json
import requests


# cflorka
# Dec 12, 2020
# Only works with small code from lists that are saved on server. Long generic code doesn't work

def getJSONfromURL(urlStr):
    getResponse = requests.get(urlStr)
    JSONresponse = getResponse.json()
    return JSONresponse

def getJSONfromArmyCode(armyCodeStr):
    '''
    Gets JSON from army builder based on army code passed as argument.

    Parameters
    ----------
    armyCodeStr : string
        String obtained from army builder by copying the string found under
        an army list when selecting a list which is saved on the server.

    Returns
    -------
    armyJSON : Dict/JSON Object
        JSON object returned when calling api with armyCodeStr
    '''
    url = "https://api.corvusbelli.com/army/lists/{}".format(armyCodeStr)
    armyJSON = getJSONfromURL(url)
    return getJSONfromURL(url)


def getJSONfromFactionCode(factionCodeParam):
    '''
    Gets JSON from army builder based on army code passed as argument.

    Parameters
    ----------
    factionCodeParam : string or int
        Number ID of a faction

    Returns
    -------
    armyJSON : Dict/JSON Object
        JSON object returned when calling api with factionCodeParam
    '''
    url = "https://api.corvusbelli.com/army/units/en/{}".format(factionCodeParam)
    armyJSON = getJSONfromURL(url)
    return armyJSON


def getArmyInfoDict(factionJSON, nodeStr):
    lookupDict = {}
    for data in factionJSON["filters"][nodeStr]:
        id = data["id"]
        lookupDict[id] = data
    return lookupDict


def getWeaponsDict(factionJSON):
    nodeName = "weapons"
    return getArmyInfoDict(factionJSON, nodeName)


def getSkillsDict(factionJSON):
    nodeName = "skills"
    return getArmyInfoDict(factionJSON, nodeName)


def getEquipDict(factionJSON):
    nodeName = "equip"
    return getArmyInfoDict(factionJSON, nodeName)


def getExtrasDict(factionJSON):
    nodeName = "extras"
    return getArmyInfoDict(factionJSON, nodeName)


def getUnitDict(factionRawJSON):
    unitLookupDict = {}
    for unit in factionRawJSON["units"]:
        id = unit["id"]
        unitLookupDict[id] = unit
    return unitLookupDict


def getExtrasListStr(idList, dictArg):
    extraList = []
    if idList is not None:
        for extraID in idList:
            extraObj = dictArg[extraID]
            extraName = extraObj["name"]
            extraList.append(extraName)
    extrasStr = ", ".join(extraList)
    return extrasStr


def getWeaponsListStr(unitOption, dataDictArg, extraDictArg):
    bsWeapons = []
    ccWeapons = []
    for weaponObj in unitOption["weapons"]:
        weaponID = weaponObj["id"]
        weapon = dataDictArg[weaponID]
        weaponName = weapon["name"]
        if "extra" in weaponObj:
            extraIDList = weaponObj["extra"]
            extraListStr = getExtrasListStr(extraIDList, extraDictArg)
            if len(extraListStr) > 0:
                weaponName += " ({})".format(extraListStr)
        if weapon["type"] == "BS":
            bsWeapons.append(weaponName)
        else:
            ccWeapons.append(weaponName)
    bsWeaponsStr = ", ".join(bsWeapons)
    ccWeaponsStr = ", ".join(ccWeapons)
    return (bsWeaponsStr, ccWeaponsStr)


def getUnitDataListStr(unitOption, dataTypeStr, dataDictArg, extraDictArg):
    dataList = []
    for dataObj in unitOption[dataTypeStr]:
        dataID = dataObj["id"]
        data = dataDictArg[dataID]
        dataName = data["name"]
        if "extra" in dataObj:
            extraIDList = dataObj["extra"]
            extraListStr = getExtrasListStr(extraIDList, extraDictArg)
            if len(extraListStr) > 0:
                dataName += " ({})".format(extraListStr)
        dataList.append(dataName)
    listStr = ", ".join(dataList)
    return listStr


def getSkillsListStr(unitOption, dataDictArg, extraDictArg):
    nodeName = "skills"
    return getUnitDataListStr(unitOption, nodeName, dataDictArg, extraDictArg)


def getEquipmentListStr(unitOption, dataDictArg, extraDictArg):
    nodeName = "equip"
    return getUnitDataListStr(unitOption, nodeName, dataDictArg, extraDictArg)


def buildCustomTrooperObj(origUnitObj, selectedProfileGroupID, selectedOptionID, weaponsDictArg, skillsDictArg, equipmentDictArg, extrasDictArg):
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
    for profileGroup in origUnitObj["profileGroups"]:
        if profileGroup["id"] == selectedProfileGroupID:
            name = profileGroup["isc"]
            for option in profileGroup["options"]:
                if option["id"] == selectedOptionID:
                    selectedOption = option
                    break

    newTrooperObj = {}
    swc = selectedOption["swc"]
    if swc[0] in ["+", "-"]:
        swcInt = 0.0
    else:
        swcInt = float(swc)
    pts = selectedOption["points"]
    # Get Weapons
    (bsWeaponsListStr, ccWeaponsListStr) = getWeaponsListStr(selectedOption, weaponsDictArg, extrasDictArg)
    # Get Equipment
    equipmentListStr = getEquipmentListStr(selectedOption, equipmentDictArg, extrasDictArg)
    # Get Skills
    skillsListStr = getSkillsListStr(selectedOption, skillsDictArg, extrasDictArg)
    # Get periferals
    includedList = []
    for includedOption in selectedOption["includes"]:
        quantity = includedOption["q"]
        includedProfileGroupID = includedOption["group"]
        includedOptionID = includedOption["option"]
        includedObj = buildCustomTrooperObj(origUnitObj, includedProfileGroupID, includedOptionID, weaponsDictArg, skillsDictArg, equipmentDictArg, extrasDictArg)
        if quantity and quantity > 1:
            oldName = includedObj["name"]
            includedObj["name"] = "{}x {}".format(quantity, oldName)
        includedList.append(includedObj)
    # Build new object
    newTrooperObj["name"] = name
    newTrooperObj["bsWeapons"] = bsWeaponsListStr
    newTrooperObj["ccWeapons"] = ccWeaponsListStr
    newTrooperObj["equipment"] = equipmentListStr
    newTrooperObj["skills"] = skillsListStr
    newTrooperObj["swc"] = swc
    newTrooperObj["swcInt"] = swcInt
    newTrooperObj["points"] = pts
    newTrooperObj["includes"] = includedList
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

    armyListRawJSON = getJSONfromArmyCode(armyCodeStr)
    # Get faction data
    factionCode = armyListRawJSON["faction"]
    factionRawJSON = getJSONfromFactionCode(factionCode)
    unitDict = getUnitDict(factionRawJSON)
    weaponsDict = getWeaponsDict(factionRawJSON)
    skillsDict = getSkillsDict(factionRawJSON)
    equipDict = getEquipDict(factionRawJSON)
    extrasDict = getExtrasDict(factionRawJSON)
    for group in armyListRawJSON["groups"]:
        groupNum = group["id"]
        groupUnitList = []
        groupSwcTotal = 0.0
        groupPtsTotal = 0
        for trooper in group["options"]:
            # Grab data from armyListFullJSON
            unitID = trooper["unit"]
            position = trooper["id"]
            profileGroupID = trooper["profileGroup"]
            optionID = trooper["option"]
            # Grab data from factionRawJSON
            rawUnitData = unitDict[unitID]
            trooperData = buildCustomTrooperObj(rawUnitData, profileGroupID, optionID, weaponsDict, skillsDict, equipDict, extrasDict)
            # BOOKMARK
            groupSwcTotal += trooperData["swcInt"]
            groupPtsTotal += trooperData["points"]
            groupUnitList.append(trooperData)
        # Build group Object
        groupObject = {}
        groupObject["name"] = "Group {}".format(groupNum)
        groupObject["swc"] = groupSwcTotal
        groupObject["points"] = groupPtsTotal
        groupObject["orders"] = getGroupOrders(groupNum, armyListRawJSON)
        groupObject["units"] = groupUnitList
        armyGroupList.append(groupObject)
    # Build Army Object
    armyObject = {}
    armyObject["name"] = armyListRawJSON["name"]
    armyObject["faction"] = armyListRawJSON["factionSlug"]
    armyObject["maxSwc"] = armyListRawJSON["verify"]["swc"]["max"]
    armyObject["swc"] = armyListRawJSON["verify"]["swc"]["total"]
    armyObject["maxPts"] = armyListRawJSON["verify"]["points"]["max"]
    armyObject["points"] = armyListRawJSON["verify"]["points"]["total"]
    armyObject["Groups"] = armyGroupList
    armyJSON = json.dumps(armyObject, indent=2)
    return armyJSON

# Test code below
# with open("testOutput.json", "w") as write_file:
    # outputString = getArmyDataFromCode("g6wpsm4Seh")
    # outputString = getArmyDataFromCode("Uj8CvHOBuh")
    # outputString = getArmyDataFromCode("U7ArcMVHE1")
    # outputString = getArmyDataFromCode("6uF5Frd26B")
    # outputString = getArmyDataFromCode("jl3L7N13m0")
    # outputString = getArmyDataFromCode("gyEFdG9oYWEDQWNxgSwCAQoAgxYBi94AAIKTAQEAAIKNAQEAAIKHAYjEAACCjQEBAACCzwEDAACCzwEDAACFGwEBAACFHAEBAACFHAEDAAIFAIKSAQIAAIKMAQYAAIKMAQYAAIMXAQMAAIMXAQMA")
    # outputString = getArmyDataFromCode("gyEFdG9oYWEBIIEsAQEBAIKTAQEA")
    # write_file.write(outputString)
