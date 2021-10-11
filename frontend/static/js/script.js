var message = "refetching data in:"
var startTime = 60;
var paused    = false;
async function getJsonData()
{
    paused = true;
    const rawResponse = await fetch('/coins/bought')
    const content     = await rawResponse.json();
    if(content["error"]){
        message = content["message"]
        timemessage.innerHTML = message
    paused = false
    startTime = 60;
    timemessage.innerHTML = message
    }
    else{
    sortData(content);
    }
}
function sortData(content){
   let data = [];
   for(let coin of Object.keys(content))
   {
       const temp = content[coin]['volume']
       console.log(temp)
       data.push(content[coin])
   }
   console.log(data)
    data.sort(function(a, b) {
    return a["timestamp"] - b["timestamp"];
    });
    displayData(data)

}
function displayData(data){
    removeAllRowBuy()
    removeAllRowSold()
    for(let i=0; i< data.length; i++){
        dataToInsert = "";
		dataToInsert += "<tr>"
        const symbol = data[i]["symbol"];
        const bought_at   = data[i]["bought_at"];
        const volume      = data[i]["volume"];
        const take_profit = data[i]["take_profit"];
        const profit = data[i]["profit"];
        const c_profit = data[i]["c_profit"];
        var b_profit   = (c_profit / bought_at) -1 
        dataToInsert += '<td style="color:#9a6cff; padding-left:28px; text-align:left"><a href="https://www.binance.com/en-IN/trade/' + symbol +'" target="_blank">'+ symbol +'</a></td>'; 
		dataToInsert += '<td style="color:#49c279">'+ bought_at+ '</td>'
		dataToInsert += '<td style="color:#ddb785">'+ volume+ '</td>'
        if(data[i]["sold"]){
            if(parseFloat(profit) < 0){
		       dataToInsert += '<td style="color:red">' + parseFloat(profit).toFixed(4)+ '%</td>'
            }
            else{
		       dataToInsert += '<td style="color:#49c279">' + parseFloat(profit).toFixed(4)+ '%</td>'
            }
		dataToInsert += '<td><button onclick="purge(\''+symbol+'\')" class="action_btn">purge</button></td>'
		dataToInsert += '</tr>'
        $('#tbody-sold').append(dataToInsert)
        }
        else{
            if(b_profit < 0){
		dataToInsert += '<td style="color:red">'+ (b_profit * 100).toFixed(4)+ '%</td>'
            }else{
		dataToInsert += '<td style="color:#49c279">'+ (b_profit *100).toFixed(4) + '%</td>'
            }
		dataToInsert += '<td><button onclick="sell(\''+symbol+'\')" class="action_btn">sell</button></td>'
		dataToInsert += '</tr>'
        $('#tbody-buy').append(dataToInsert)
        }
    }
    paused = false
    startTime = 60;
    timemessage.innerHTML = message
}
const timemessage = document.getElementById("timermessage");
timemessage.innerHTML = message
getJsonData()



setInterval(function() {
const timer = document.getElementById("counter")
    if(!paused){
    if (startTime == 0){
        timer.innerHTML = "Fetching ...."
        paused = true;
        console.log("paused")
        getJsonData()
    }
    else{
        if(startTime / 10 < 1){
            startTime = '0'+ startTime
        }
        timer.innerHTML = ' 00:'+ startTime
        startTime -=1
    }
}
},1000) // run every seconds

async function sell(symbol){
    pause = true;
    timemessage.innerHTML = "selling ... "
    const rawResponse = await fetch('coins/sell', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({symbol:symbol})
  });
  const content = await rawResponse.json();

  if (content["status"] == '1'){
      getJsonData()
  }
  message = content["message"]
    timemessage.innerHTML = message
}

async function purge(symbol){
    const rawResponse = await fetch('coins/purge', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({symbol:symbol})
  });
  const content = await rawResponse.json();

  if (content["status"] == '1'){
      getJsonData()
  }
  message = content["message"]
    timemessage.innerHTML = message
}

function removeAllRowSold(){
var elmtTable = document.getElementById('tbody-sold');
var tableRows = elmtTable.getElementsByTagName('tr');
var rowCount = tableRows.length;

for (var x=rowCount-1; x>-1; x--) {
   elmtTable.removeChild(tableRows[x]);
} 
  }

function removeAllRowBuy(){
var elmtTable = document.getElementById('tbody-buy');
var tableRows = elmtTable.getElementsByTagName('tr');
var rowCount = tableRows.length;

for (var x=rowCount-1; x>-1; x--) {
   elmtTable.removeChild(tableRows[x]);
} 
  }