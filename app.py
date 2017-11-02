from flask import Flask,render_template, request, redirect,url_for,jsonify
from urllib2 import urlopen
from bs4 import BeautifulSoup as Bsoup
import pysolr
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import re
import subprocess
import platform
import time 
import os

app = Flask(__name__, template_folder = 'templates')

def checkSolr():
	solr = pysolr.Solr('http://127.0.0.1:8983/solr/AdaptiveWeb', timeout = 100)
	try:
		res = solr.search(q="*:*",rows=10)
		if len(res)>1:
			return True
		else:
			return False
	except:
		return False

def createScraper():
	base_url = 'https://en.wikibooks.org'
	x = urlopen(base_url+"/wiki/Java_Programming")
	soup = Bsoup(x, 'html.parser')
	allAtags = soup.findAll('a')

	scraperList =[]
	# id ,url, title, text
	# bin/solr start
	# bin/solr create -c AdaptiveWeb
	count = 0
	for i in range(28,204):
		print i
		item = {}

		href = allAtags[i]['href']
		title = allAtags[i]['title']

		if "Help" not in href:
			# item['title']=title
			newUrl = base_url+href
			item['url']=newUrl
			# getText function
			tempx = urlopen(newUrl)
			soup = Bsoup(tempx, 'html.parser')
			pageTitle = soup.find('h1',{'id':'firstHeading'}).getText()
			introductionText = ""
			intoductionSection = soup.find('table',{'class':'wikitable'})
			introductionHtml = ""
			if intoductionSection:
				siblings = intoductionSection.next_siblings
				for sib in siblings:
					if(sib.name == 'h2'):
						break
					else:
						try:
							introductionText = introductionText+sib.text
							introductionHtml = introductionHtml+str(sib)
						except:
							pass
			if introductionText is not "":
				item = {}
				item['url']=newUrl
				item['text']=introductionText
				item['title']=pageTitle+" Introduction"
				item['id'] = count
				item['split']=introductionText
				item['htmlContent']=introductionHtml
				count+=1
				scraperList.append(item)

			textDiv = soup.find('div',{'id':'mw-content-text'})
			allH2tags = textDiv.findAll('h2')
			numH2tags = len(allH2tags)
			for j in range(numH2tags-1):
				h2title = allH2tags[j].getText()
				h2title = h2title.replace('[edit]','')
				textunderH2 = ""
				htmlunderH2 = ""
				siblings = allH2tags[j].next_siblings
				for sib in siblings:
					if(sib.name == 'h2'):
						break
					else:
						try:
							textunderH2 = textunderH2+sib.text
							htmlunderH2=htmlunderH2+str(sib)
						except:
							pass
				if textunderH2 is not "":
					item = {}
					item['url']=newUrl
					item['text']=textunderH2
					item['title']=pageTitle+" - "+h2title
					item['id'] = count
					item['split']=textunderH2
					item['htmlContent']=htmlunderH2
					count+=1
					scraperList.append(item)	

		
	num_items = len(scraperList)
	if platform.system() is 'Windows':
		response = subprocess.call("solr-7.1.0\\bin\\solr start -p 8983", shell = True)
	else:
		print "Unix"
		response = subprocess.call("solr-7.1.0/bin/solr start -p 8983", shell = True)

	try:
		solr = pysolr.Solr('http://127.0.0.1:8983/solr/AdaptiveWeb', timeout = 500)
		# response = solr.delete(q = "*:*")
		response = solr.add(scraperList)
	except:
		pass	

@app.route('/')
def index():
	if checkSolr():
		print "Solr is Live"
		return render_template('index.html')
	else:
		print "Solr is Down"
		return render_template('solr_start.html')

@app.route('/startSolr')
def startSolr():
	createScraper()
	item={}
	item['loaded']=1
	return jsonify(item)

@app.route('/getRec',methods=['POST'])
def getRec():
	queryText ={
	'1':"I was presented with this question in an end of module open book exam today and found myself lost. i was reading Head first Javaand both definitions seemed to be exactly the same. i was just wondering what the MAIN difference was for my own piece of mind. i know there are a number of similar questions to this but, none i have seen which provide a definitive answer.Thanks, Darren.",
	'2':"Inheritance is when a 'class' derives from an 	existing 'class'.So if you have a Person class, then you have a Student class that extends Person, Student inherits all the things that Person has.There are some details around the access modifiers you put on the fields/methods in Person, but that's the basic idea.For example, if you have a private field on Person, Student won't see it because its private, and private fields are not visible to subclasses.Polymorphism deals with how the program decides which methods it should use, depending on what type of thing it has.If you have a Person, which has a read method, and you have a Student which extends Person, which has its own implementation of read, which method gets called is determined for you by the runtime, depending if you have a Person or a Student.It gets a bit tricky, but if you do something likePerson p = new Student();p.read();the read method on Student gets called.Thats the polymorphism in action.You can do that assignment because a Student is a Person, but the runtime is smart enough to know that the actual type of p is Student.Note that details differ among languages.You can do inheritance in javascript for example, but its completely different than the way it works in Java.",
	'3':"Polymorphism: The ability to treat objects of different types in a similar manner.Example: Giraffe and Crocodile are both Animals, and animals can Move.If you have an instance of an Animal then you can call Move without knowing or caring what type of animal it is.Inheritance: This is one way of achieving both Polymorphism and code reuse at the same time.Other forms of polymorphism:There are other way of achieving polymorphism, such as interfaces, which provide only polymorphism but no code reuse (sometimes the code is quite different, such as Move for a Snake would be quite different from Move for a Dog, in which case an Interface would be the better polymorphic choice in this case.In other dynamic languages polymorphism can be achieved with Duck Typing, which is the classes don't even need to share the same base class or interface, they just need a method with the same name.Or even more dynamic like Javascript, you don't even need classes at all, just an object with the same method name can be used polymorphically.",
	'4':"I found out that the above piece of code is perfectly legal in Java. I have the following questions. ThanksAdded one more question regarding Abstract method classes. public class TestClass {public static void main(String[] args) {TestClass t = new TestClass();}private static void testMethod(){abstract class TestMethod{int a;int b;int c;abstract void implementMe();}class DummyClass extends TestMethod{void implementMe(){}}DummyClass dummy = new DummyClass();}}",
	'5': "In java it's a bit difficult to implement a deep object copy function. What steps you take to ensure the original object and the cloned one share no reference? ",
	'6':"You can make a deep copy serialization without creating some files. Copy: Restore: ByteArrayOutputStream bos = new ByteArrayOutputStream();ObjectOutputStream oos = new ObjectOutputStream(bos);oos.writeObject(object);oos.flush();oos.close();bos.close();byte[] byteData = bos.toByteArray();; ByteArrayInputStream bais = new ByteArrayInputStream(byteData);(Object) object = (Object) new ObjectInputStream(bais).readObject();",
	'7':"Java has the ability to create classes at runtime. These classes are known as Synthetic Classes or Dynamic Proxies. See for more information. Other open-source libraries, such as and also allow you to generate synthetic classes, and are more powerful than the libraries provided with the JRE. Synthetic classes are used by AOP (Aspect Oriented Programming) libraries such as Spring AOP and AspectJ, as well as ORM libraries such as Hibernate.",
	'8':"A safe way is to serialize the object, then deserialize.This ensures everything is a brand new reference.about how to do this efficiently. Caveats: It's possible for classes to override serialization such that new instances are created, e.g. for singletons.Also this of course doesn't work if your classes aren't Serializable.",
	'9':"comment this code /*if (savedinstancestate == null) {     getsupportfragmentmanager().begintransaction()             .add(r.id.container  new placeholderfragment())             .commit(); }*/ ",
	'10':"in a class i can have as many constructors as i want with different argument types. i made all the constructors as private it didn't give any error because my implicit default constructor was public but when i declared my implicit default constructor as private then its showing an error while extending the class.  why?       this works fine         this can not be inherited      public class demo4  {     private string name;     private int age;     private double sal;      private demo4(string name  int age) {         this.name=name;         this.age=age;        }      demo4(string name) {         this.name=name;     }      demo4() {         this(\"unknown\"  20);         this.sal=2000;     }      void show(){         system.out.println(\"name\"+name);         system.out.println(\"age: \"+age);     } }  public class demo4  {     private string name;     private int age;     private double sal;      private demo4(string name  int age) {         this.name=name;         this.age=age;     }      demo4(string name) {         this.name=name;     }      private demo4() {         this(\"unknown\"  20);         this.sal=2000;     }      void show() {         system.out.println(\"name\"+name);         system.out.println(\"age: \"+age);     } }  ",
	}
	reqData = request.form
	reqID = reqData['id']
	reqText = queryText[str(reqID)]

	ps = PorterStemmer()

	words = re.split('\W+',reqText)
	wordList = [word for word in words if word not in stopwords.words('english')]
	wordList = [ps.stem(word) for word in wordList]

	query =' or '.join(wordList)

	q = "split: (" + query+")"

	solr = pysolr.Solr('http://127.0.0.1:8983/solr/AdaptiveWeb', timeout = 100)
	results = solr.search(q = q, rows = 10)
	resultDict = []

	for res in results:
		item={}
		item['url'] = res['url']
		item['title']=res['title']
		item['text'] =res['text']
		item['id'] = res['id']
		item['htmlContent']=res['htmlContent']
		resultDict.append(item)

	return jsonify(resultDict)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)