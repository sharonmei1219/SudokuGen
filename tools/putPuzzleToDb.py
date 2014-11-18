from com.ziclix.python.sql import zxJDBC
import java.lang.reflect.Method 
import java.lang.ClassLoader as javaClassLoader 
from java.lang import Object as javaObject 
from java.io import File as javaFile 
from java.net import URL as javaURL 
from java.net import URLClassLoader 
import jarray 
import sys
# from com.xhaus.jyson import JysonCodec as json

url = "jdbc:hsqldb:hsql://localhost/puzzles"
username = "sa"
password = "Rff36xfnd95;"

driver = "org.hsqldb.jdbcDriver"

# db = zxJDBC.connect(url, username, password, driver)


class classPathHackerTest(object): 
    """Original Author: SG Langer Jan 2007, conversion from Java to Jython 
    Updated version (supports Jython 2.5.2) >From http://glasblog.1durch0.de/?p=846 
    
    Purpose: Allow runtime additions of new Class/jars either from 
    local files or URL 
    """ 
        
    def addFile(self, s): 
        """Purpose: If adding a file/jar call this first 
        with s = path_to_jar""" 
        # make a URL out of 's' 
        f = javaFile(s) 
        u = f.toURL() 
        a = self.addURL(u) 
        return a 
      
    def addURL(self, u): 
         """Purpose: Call this with u= URL for 
         the new Class/jar to be loaded""" 
         sysloader = javaClassLoader.getSystemClassLoader() 
         sysclass = URLClassLoader 
         method = sysclass.getDeclaredMethod("addURL", [javaURL]) 
         a = method.setAccessible(1) 
         jar_a = jarray.array([u], javaObject) 
         b = method.invoke(sysloader, [u])
         return u 

try :
    db = zxJDBC.connect(url, username, password, driver)
except:
    jarLoad = classPathHackerTest()
    a = jarLoad.addFile("./hsqldb.jar")
    db = zxJDBC.connect(url, username, password, driver)
    c = db.cursor()

    inputf = open("e:/puzzle.txt", "r")
    puzzleId = 0
    # print(inputf.readline())
    for line in inputf:
        print(line)
        c.execute("insert into evilpuzzle values (?,?)", [puzzleId, line])
        puzzleId += 1
        # c.execute("insert into evilpuzzle values (?,?)", [1002, 'jason'])
    db.commit()
