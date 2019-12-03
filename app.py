from flask import Flask, render_template, flash
from forms import SearchForm, ClassifierForm
import numpy
import json

# Globals
app = Flask(__name__)
app.config['SECRET_KEY'] = 'u7PrtQm5Dur0cgkcyOlOmU7kYm9xy4ng'
champions = {}
bucket = []

# Constants
ASSASSIN_TOTAL = 17.0
FIGHTER_TOTAL = 39.0
MAGE_TOTAL = 32.0
MARKSMAN_TOTAL = 23.0
SUPPORT_TOTAL = 15.0
TANK_TOTAL = 19.0


# Creating the JSON
with open('ChampionDataset.json') as json_file:
    champions = json.load(json_file)

# Creating a bucket of words
for champion in champions:
    # text = champion["Name"] + " " + champion["Title"] + " " + champion["Title"] + " " + champion["Title"] + " " + champion["Title"] + " " + champion["Title"]
    bucket.append(champion["Name"])
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Title"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Role"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Region"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1] + " " + champion["Bio"]
    bucket[len(bucket) - 1] = bucket[len(bucket) - 1].upper()


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title="Home")


@app.route('/classifier', methods=['GET', 'POST'])
def classifier():
    form = ClassifierForm()
    if form.validate_on_submit():
        # print('Inputs: {0}\n'.format(form.classifierInput._value()))
        classifierInputs = form.classifierInput._value().split()
        roleProbability = classify(classifierInputs)
        return render_template('classifier.html', title="Classifier", form=form, roleProbability=roleProbability)
    else:
        return render_template('classifier.html', title="Classifier", form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():

        # Splitting search terms
        searchInputs = form.searchInput._value().split()

        # Calculating top 5
        topFive = create_tf_matrix(searchInputs)
        return render_template('search.html', title="Search", form=form, topFive=topFive)
    else:
        flash(f'{form.searchInput} is not valid', 'error')
        return render_template('search.html', title="Search", form=form)


def classify(classifierInputs):
    championCount = len(bucket)

    # Lists for each classifier role
    assassinList = []
    fighterList = []
    mageList = []
    marksmanList = []
    supportList = []
    tankList = []

    # Creating the role lists
    for champion in champions:
        role = champion["Role"]

        if role == "FIGHTER":
            fighterList.append(champion)
        elif role == "SUPPORT":
            supportList.append(champion)
        elif role == "MAGE":
            mageList.append(champion)
        elif role == "MARKSMAN":
            marksmanList.append(champion)
        elif role == "ASSASSIN":
            assassinList.append(champion)
        elif role == "TANK":
            tankList.append(champion)

    # List to hold the number of occurences for each term, given each role
    assassinOccurences = []
    fighterOccurences = []
    mageOccurences = []
    marksmanOccurences = []
    supportOccurences = []
    tankOccurences = []

    # Keeping count for probabilities at the end
    assassinCount = len(assassinList)
    fighterCount = len(fighterList)
    mageCount = len(mageList)
    marksmanCount = len(marksmanList)
    supportCount = len(supportList)
    tankCount = len(tankList)

    print("Assassing count before: {0}\n".format(assassinCount))
    # Assassin Loop
    for term in classifierInputs:
        occurrences = 0
        for champion in assassinList:
            if term.upper() in champion["Bio"].upper():
                occurrences += 1
        termData = {
            "Term": term,
            "Occurrences": occurrences
        }

        # Smoothing
        if occurrences == 0:
            championCount += 1
            assassinCount += 1
            termData["Occurrences"] = 1
        assassinOccurences.append(termData)

    # Fighter Loop
    for term in classifierInputs:
        occurrences = 0
        for champion in fighterList:
            if term.upper() in champion["Bio"].upper():
                occurrences += 1

        termData = {
            "Term": term,
            "Occurrences": occurrences
        }

        # Smoothing
        if occurrences == 0:
            championCount += 1
            fighterCount += 1
            termData["Occurrences"] = 1

        fighterOccurences.append(termData)

    # Mage Loop
    for term in classifierInputs:
        occurrences = 0
        for champion in mageList:
            if term.upper() in champion["Bio"].upper():
                occurrences += 1

        termData = {
            "Term": term,
            "Occurrences": occurrences
        }

        # Smoothing
        if occurrences == 0:
            championCount += 1
            mageCount += 1
            termData["Occurrences"] = 1
        mageOccurences.append(termData)

    # Marksman Loop
    for term in classifierInputs:
        occurrences = 0
        for champion in marksmanList:
            if term.upper() in champion["Bio"].upper():
                occurrences += 1

        termData = {
            "Term": term,
            "Occurrences": occurrences
        }

        # Smoothing
        if occurrences == 0:
            championCount += 1
            marksmanCount += 1
            termData["Occurrences"] = 1

        marksmanOccurences.append(termData)

    # Support Loop
    for term in classifierInputs:
        occurrences = 0
        for champion in supportList:
            if term.upper() in champion["Bio"].upper():
                occurrences += 1

        termData = {
            "Term": term,
            "Occurrences": occurrences
        }

        # Smoothing
        if occurrences == 0:
            championCount += 1
            supportCount += 1
            termData["Occurrences"] = 1

        supportOccurences.append(termData)

    # Tank Loop
    for term in classifierInputs:
        occurrences = 0
        for champion in tankList:
            if term.upper() in champion["Bio"].upper():
                occurrences += 1

        termData = {
            "Term": term,
            "Occurrences": occurrences
        }

        # Smoothing
        if occurrences == 0:
            championCount += 1
            tankCount += 1
            termData["Occurrences"] = 1

        tankOccurences.append(termData)

    probAssassin = 0.0
    probNotAssassin = 0.0
    probFighter = 0.0
    probNotFighter = 0.0
    probMage = 0.0
    probNotMage = 0.0
    probMarksman = 0.0
    probNotMarksman = 0.0
    probSupport = 0.0
    probNotSupport = 0.0
    probTank = 0.0
    probNotTank = 0.0

    # Assassin Probability Calcuations
    for termData in assassinOccurences:
        probAssassin += (termData["Occurrences"] / assassinCount)
    for (f, mage, mark, supp, tank) in zip(fighterOccurences, mageOccurences, marksmanOccurences, supportOccurences, tankOccurences):
        probNotAssassin += ((f["Occurrences"] + mage["Occurrences"] + mark["Occurrences"] + supp["Occurrences"] + tank["Occurrences"])/(championCount - assassinCount))

    probAssassin += (assassinCount / championCount)
    probNotAssassin += ((championCount - assassinCount) / championCount)
    probAssassin = probAssassin / probNotAssassin

    # Fighter Probability Calcuations
    for termData in fighterOccurences:
        probFighter += (termData["Occurrences"] / fighterCount)
    for (ass, mage, mark, supp, tank) in zip(assassinOccurences, mageOccurences, marksmanOccurences, supportOccurences, tankOccurences):
        probNotFighter += ((ass["Occurrences"] + mage["Occurrences"] + mark["Occurrences"] + supp["Occurrences"] + tank["Occurrences"]) / (championCount - fighterCount))

    probFighter += (fighterCount / championCount)
    probNotFighter += ((championCount - fighterCount) / championCount)
    probFighter = probFighter / probNotFighter;

    # Mage Probability Calcuations
    for termData in mageOccurences:
        probMage += (termData["Occurrences"] / mageCount)
    for (f, ass, mark, supp, tank) in zip(fighterOccurences, assassinOccurences, marksmanOccurences, supportOccurences, tankOccurences):
        probNotMage += ((f["Occurrences"] + ass["Occurrences"] + mark["Occurrences"] + supp["Occurrences"] + tank["Occurrences"]) / (championCount - mageCount))

    probMage += (mageCount / championCount)
    probNotMage += ((championCount - mageCount) / championCount)
    probMage = probMage / probNotMage

    # Marksman Probability Calcuations
    for termData in marksmanOccurences:
        probMarksman += (termData["Occurrences"] / marksmanCount)
    for (f, mage, ass, supp, tank) in zip(fighterOccurences, mageOccurences, assassinOccurences, supportOccurences, tankOccurences):
        probNotMarksman += ((f["Occurrences"] + mage["Occurrences"] + ass["Occurrences"] + supp["Occurrences"] + tank["Occurrences"]) / (championCount - marksmanCount))

    probMarksman += (marksmanCount / championCount)
    probNotMarksman += ((championCount - marksmanCount) / championCount)
    probMarksman = probMarksman / probNotMarksman

    # Support Probability Calcuations
    for termData in supportOccurences:
        probSupport += (termData["Occurrences"] / supportCount)
    for (f, mage, mark, ass, tank) in zip(fighterOccurences, mageOccurences, marksmanOccurences, assassinOccurences, tankOccurences):
        probNotSupport += ((f["Occurrences"] + mage["Occurrences"] + mark["Occurrences"] + ass["Occurrences"] + tank["Occurrences"]) / (championCount - supportCount))

    probSupport += (supportCount / championCount)
    probNotSupport += ((championCount - supportCount) / championCount)
    probSupport = probSupport / probNotSupport

    # Tank Probability Calcuations
    for termData in tankOccurences:
        probTank += (termData["Occurrences"] / tankCount)
    for (f, mage, mark, supp, ass) in zip(fighterOccurences, mageOccurences, assassinOccurences, supportOccurences, tankOccurences):
        probNotTank += ((f["Occurrences"] + mage["Occurrences"] + mark["Occurrences"] + supp["Occurrences"] + ass["Occurrences"]) / (championCount - tankCount))

    probTank += (tankCount / championCount)
    probNotTank += ((championCount - tankCount) / championCount)
    probTank = probTank / probNotTank

    # Normalizing probabilities to add up to 100%
    probTotal = probAssassin + probFighter + probMage + probMarksman + probSupport + probTank
    normAssassin = (probAssassin / probTotal) * 100
    normFighter = (probFighter / probTotal) * 100
    normMage = (probMage / probTotal) * 100
    normMarksman = (probMarksman / probTotal) * 100
    normSupport = (probSupport / probTotal) * 100
    normTank = (probTank / probTotal) * 100

    return {"Assassin": normAssassin,
            "ProbAssassin": probAssassin,
            "ProbNotAssassin": probNotAssassin, 
            "Fighter": normFighter,
            "ProbFighter": probFighter,
            "ProbNotFighter": probNotFighter, 
            "Mage": normMage,
            "ProbMage": probMage,
            "ProbNotMage": probNotMage,
            "Marksman": normMarksman,
            "ProbMarksman": probMarksman,
            "ProbNotMarksman": probNotMarksman, 
            "Support": normSupport,
            "ProbSupport": probSupport,
            "ProbNotSupport": probNotSupport, 
            "Tank": normTank,
            "ProbTank": probTank,
            "ProbNotTank": probNotTank }


def create_tf_matrix(searchInputs):
    bucketLength = len(bucket)
    championsSorted = champions[:]  # Copy without reference
    topFive = []                    # Used as the return variable

    for championIndex in range(len(championsSorted)):
        wordDataArray = []          # Number of documents the term appears in
        score = 0                   # Total score per document

        for termIndex in range(len(searchInputs)):

            # Calculates the number of documents that contain the term
            docTermFrequency = getTermCount(searchInputs[termIndex])

            #Calculate TF for term
            tf = bucket[championIndex].count(searchInputs[termIndex].upper()) / len(bucket[championIndex])

            # Calculate IDF for term
            if docTermFrequency == 0:
                idf = 0
            else:
                idf = numpy.log(bucketLength / docTermFrequency)

            # Calculate TF-IDF total
            score = score + (tf * idf)

            # Creating word data for array
            wordData = {
                "Term": searchInputs[termIndex],
                "Frequency": docTermFrequency,
                "Tf": tf,
                "Idf": idf,
                "Index": championIndex
            }
            wordDataArray.append(wordData)

        championsSorted[championIndex]["WordData"] = wordDataArray
        championsSorted[championIndex]["Score"] = score

    # Sorting the list so the highest scores are first
    championsSorted.sort(key=lambda x: x['Score'], reverse=True)

    # Grabbing top 5 results
    for i in range(0, 5):
        topFive.append(championsSorted[i])

    return topFive


def getTermCount(term):
    result = 0
    for doc in bucket:
        tf = doc.count(term.upper())
        if tf > 0:
            result += 1
    return result


if __name__ == '__main__':
    app.run(debug=True)
