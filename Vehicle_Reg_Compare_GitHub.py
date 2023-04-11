import os
import pandas as pd
import re
import time
from selenium import webdriver as wb
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException as NE

# Define input folder containing all input files.
inputPath = r"<<User inputs the path to input files>>"

# Define output file.
outputPath = r"<<User inputs the patch to output files along with filename>>"

# Declare variable as array to capture all registration numbers from input files.
carRegList = []

# Function to Read all input text file

def input_car_reg_list(inputPath):
    for file in os.listdir(inputPath):
        if file.endswith('.txt'):
            # Creating input file path
            filePath = f"{inputPath}/{file}"
            print('Reading file--', filePath)
            with open(filePath, 'r') as f:
                fileContents = f.read()
                regex = r'^([A-Z]{3}\s?(\d{3}|\d{2}|d{1})\s?[A-Z])|([A-Z][A-Z]\s?(\d{3}|\d{2}|\d{1})\s?[A-Z]{3})|(([A-HK-PRSVWY][A-HJ-PR-Y])\s?([0][2-9]|[1-9][0-9])\s?[A-HJ-PR-Z]{3})$'
                pattern = re.compile(regex)
                carReg = re.findall(pattern, fileContents, flags = 0)
                carReg = [tuple(filter(None, x)) for x in carReg]
                for x in carReg:
                    for i in x:
                        i = i.replace(" ","")
                        if not i.isdigit():
                            carRegList.append(i)
    return carRegList

# Call input_car_reg_list function and parse inputPath to get combined vehicle registration list
carRegFinalList = []
carRegFinalList = input_car_reg_list(inputPath)

driver = wb.Chrome(executable_path="<<path where chromedriver.exe exists>>chromedriver.ex")
time.sleep(2)

# Launch cazoo
driver.get("https://www.cazoo.co.uk/value-my-car/")
time.sleep(2)

driver.maximize_window()
time.sleep(2)

# Accept cookies
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[1]/div[2]/div/div/button/span'))).click()
time.sleep(2)

# Creating an empty dataframe
resultSetDF = pd.DataFrame(columns=['REGISTRATION', 'EXPECTED MAKE', 'ACTUAL MAKE', 'EXPECTED MODEL', 'ACTUAL MODEL', 'TEST STATUS'])

# Add for loop for parsing through each vehicle registration number

for i in carRegFinalList:
# Launch cazoo again
    driver.get("https://www.cazoo.co.uk/value-my-car/")
    time.sleep(2)
# Find and Input Vehicle Registration Number
    driver.find_element(By.XPATH, '//*[@id="vrm"]').send_keys(i);
    time.sleep(2)
# Click on Start Valuation
    driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[2]/div/div/div/article/div[2]/div/form/button/span').click();
    time.sleep(5)

# Check if output exists using xpath
    try:
        output = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div[2]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/p[2]').text

        splitOutput = output.split(":")[1]
        splitOutput = splitOutput.lstrip()

        actualMake = splitOutput.split(' ', 1)[0]
        actualMake = actualMake.strip()
        actualModel = splitOutput.split(' ', 1)[1]
        actualModel = actualModel.strip()

# Search for i in given output file
        xPathExistsFlag = 1
        searchfile = open(outputPath, "r")
        for line in searchfile:
            if i in line:
                fullRegDetails = line
                xPathExistsFlag = 0
        searchfile.close()

        if xPathExistsFlag == 0:
            # Scenario 1 and 4 from output scenario analysis
            fullRegDetails = fullRegDetails.split(",", 1)[1]
            expectedMake = fullRegDetails.split(",", 1)[0]
            expectedMake = expectedMake.strip()
            expectedModel = fullRegDetails.split(",", 1)[1]
            expectedModel = expectedModel.strip()
            # Compare Input and Output values
            if actualMake == expectedMake and actualModel == expectedModel:
                # Scenario 1
                testResult01 = 'PASS'
                # Consolidating compare results and adding it to DataFrame
                tc01List = [i, expectedMake, actualMake, expectedModel, actualModel, testResult01]
                resultSetDF.loc[len(resultSetDF)] = tc01List
            else:
                # Scenario 4
                testResult04 = 'FAIL'
                # Consolidating compare results and adding it to DataFrame
                tc04List = [i, expectedMake, actualMake, expectedModel, actualModel, testResult04]
                resultSetDF.loc[len(resultSetDF)] = tc04List

        else:
            # Scenario 3 from output scenario analysis
            expectedModel03 = "Given output info not available"
            expectedMake03 = "Given output info not available"
            testResult03 = 'FAIL'
            tc03List = [i, expectedMake03, actualMake, expectedModel03, actualModel, testResult03]
            resultSetDF.loc[len(resultSetDF)] = tc03List

# Go here if xpath is not found
    except NE:
        xPathNotExistsFlag = 1
        searchfile = open(outputPath, "r")
        for line in searchfile:
            if i in line:
                fullRegDetails02 = line
                xPathNotExistsFlag = 0
        searchfile.close()

        if xPathNotExistsFlag == 0:
            # Scenario 2 from output scenario analysis
            actualModel02 = "Input reg details not available on website"
            actualMake02 = "Input reg details not available on website"
            fullRegDetails02 = fullRegDetails02.split(",", 1)[1]
            expectedMake02 = fullRegDetails02.split(",", 1)[0]
            expectedMake02 = expectedMake02.strip()
            expectedModel02 = fullRegDetails02.split(",", 1)[1]
            expectedModel02 = expectedModel02.strip()
            testResult02 = 'FAIL'
            tc02List = [i, expectedMake02, actualMake02, expectedModel02, actualModel02, testResult02]
            resultSetDF.loc[len(resultSetDF)] = tc02List

        else:
            # Scenaio 5 in output scenario analysis
            actualModel05 = "Input reg details not available on website"
            actualMake05 = "Input reg details not available on website"
            expectedModel05 = "Given output info not available"
            expectedMake05 = "Given output info not available"
            testResult05 = 'FAIL'
            tc05List = [i, expectedMake05, actualMake05, expectedModel05, actualModel05, testResult05]
            resultSetDF.loc[len(resultSetDF)] = tc05List

#print(resultSetDF)

totalTests=len(resultSetDF.index)
totalPass=len(resultSetDF[resultSetDF["TEST STATUS"]=="PASS"])
totalFail=len(resultSetDF[resultSetDF["TEST STATUS"]=="FAIL"])
print("Total Number of Tests", totalTests)
print("Total Number of Test Cases Passed", totalPass)
print("Total Number of Test Cases Failed", totalFail)

# Writing to html file
with open('test_results.html', 'w') as html_file:
    html_file.write(resultSetDF.to_html())
