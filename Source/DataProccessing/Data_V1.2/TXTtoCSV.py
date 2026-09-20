def setWorkingDirToThis():
    from pathlib import Path
    import os

    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

def getAllFilesInWD():
    from pathlib import Path
    files = [p.name for p in Path.cwd().iterdir() if p.is_file()]
    return files

def filterFiles(files, prefix):
    #filter files by prefix
    filtered = []
    for file in files:
        if file[0:len(prefix)] == prefix:
            filtered.append(file)

    return filtered

def TxtToCSV(csvName, shouldAccumulate, prefix):
    import csv

    #set working dir
    setWorkingDirToThis()

    #get all files within this working dir
    files = getAllFilesInWD()

    #filter to only data files
    filtered = filterFiles(files, prefix)

    #go through each instance and compile into 1 csv line(format per instance: ["pp", "cgol", "", "400", "1", ["<time1>", "<time2>" ...]]; format per set: [instance1, instance2, ...])
    data = []
    for file in filtered:
        instanceData = []
        #get language, logic and size
        nameData = file.split("_")
        
        #replace "" with "None"
        for i in range(len(nameData)):
            if nameData[i] == "":
                nameData[i] = "None"

        for dt in nameData:
            if dt != prefix:    #dont store prefix
                instanceData.append(dt)

        #get contents
        contents = []
        with open(file, "r", encoding="utf-8") as file:
            contents = file.read().splitlines()

        #round to 4 decimals
        for i in range(len(contents)):
            contents[i] = round(float(contents[i]), 4)

        #accumulate if neccesary
        if shouldAccumulate:
            accumulated = []
            currAccum = 0
            for content in contents:
                currAccum += content
                accumulated.append(currAccum)

            #replace periter data with accumulated
            contents = accumulated

        #add to instance data, add to all data
        instanceData.append(contents)
        data.append(instanceData)

    #write data to csv
    with open(csvName, "w", newline="\n", encoding="utf-8") as f:
        for dta in data:
            writer = csv.writer(f)
            writer.writerow(dta)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#acctualy run the conversion
TxtToCSV("csv_periter.csv", False, "data")
TxtToCSV("csv_accumulated.csv", True, "data")