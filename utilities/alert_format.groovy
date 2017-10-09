import static com.xlson.groovycsv.CsvParser.parseCsv
import java.util.*
import java.io.*

def bw = new BufferedWriter(new FileWriter("/home/user/proofer_alerts.txt", true));
//oven_alarms.csv
def csva = parseCsv(new FileReader("/home/user/Downloads/groovy-2.4.12/proofer_alerts.csv"))
def firstTime = true
def s = ""
csva.each {  
    if (firstTime){
        s = it[3]
        firstTime = false
        bw.write "{\"" + it[3] + "\" : {\"" + it[4] + "\": [\"" + it[0] + "\",\"" + it[1] + "\"]"
    }else{
        if (s == it[3]){
            bw.write ",\"" + it[4] + "\": [\"" + it[0] + "\",\"" + it[1] + "\"]"
        }else{
            bw.write "},\"" + it[3] + "\" : {\"" + it[4] + "\": [\"" + it[0] + "\",\"" + it[1] + "\"]"
            s = it[3]
        }
    
    }  
    //bw.newLine()
    //bw.write "\"" + it[3] + "\" : {\"" + 0 + "\": [\"" + it[0] + "\",\"" + it[1] + "\"]},"
    bw.newLine()
}
bw.write "}}"
bw.newLine()
bw.flush()
bw.close()


/*
//Add section for alerts
def bw = new BufferedWriter(new FileWriter("/home/user/proofer_model_update.txt", true))
def csva = parseCsv(new FileReader("/home/user/Downloads/groovy-2.4.12/proofer_alerts.csv"))
bw.write "{\"alerts\": ["
csva.each {
    bw.write "{\"name\":\"" + it[0] + "\", \"severity\":" + it[2] + "},"
    //bw.newLine()
}
bw.write "]}"
bw.flush()
bw.close()
*/