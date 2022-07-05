//Global chart options
Chart.defaults.borderColor = '#333';    
Chart.defaults.elements.line.fill = false;
Chart.defaults.elements.line.tension = 0.5;

//Create the configuration for the Chart JS function
function buildChart(csvFile) {  
   
    //Function to get columns
    const arrayColumn = (arr, n) => arr.map(x => x[n]);
        
    var timeLabels = arrayColumn(csvFile,0).slice(1,-1);
    
    //Put the date and time on two lines for the graph
    timeLabels = timeLabels.map(function(t) { 
        return t.split(' - '); 
        }); 
    
    //Get all the TC columns
    var tc1Data = arrayColumn(csvFile,1).slice(1,-1);
    var tc2Data = arrayColumn(csvFile,2).slice(1,-1);
    var tc3Data = arrayColumn(csvFile,3).slice(1,-1);
    var tc4Data = arrayColumn(csvFile,4).slice(1,-1);
    var tc6Data = arrayColumn(csvFile,6).slice(1,-1);
        
    //Update the numeric text at the top of the screen
    document.getElementById("TC1").textContent=String(parseFloat(tc1Data[tc1Data.length-1]).toFixed(1)).padStart(6,'0');
    document.getElementById("TC2").textContent=String(parseFloat(tc2Data[tc2Data.length-1]).toFixed(1)).padStart(6,'0');
    document.getElementById("TC3").textContent=String(parseFloat(tc3Data[tc3Data.length-1]).toFixed(1)).padStart(6,'0');
    document.getElementById("TC4").textContent=String(parseFloat(tc4Data[tc4Data.length-1]).toFixed(1)).padStart(6,'0');
    document.getElementById("TC6").textContent=String(parseFloat(tc6Data[tc6Data.length-1]).toFixed(1)).padStart(6,'0');
    document.getElementById("LastRead").textContent=timeLabels[timeLabels.length-1];

    const data = {
        labels: timeLabels,
        datasets: [
          {
            data: tc1Data,
            borderColor: "#FF0000",
            backgroundColor: "#FF0000",
            label: "TC1",
          },
          {
            data: tc2Data,
            borderColor: "#FFAA00",
            backgroundColor: "#FFAA00",
            label: "TC2",
          },
          {
            data: tc3Data,
            borderColor: "#365BB0",
            backgroundColor: "#365BB0",
            label: "TC3",
          },
          {
            data: tc4Data,
            borderColor: "#00B366",
            backgroundColor: "#00B366",
            label: "TC4",
          },
          {
            data: tc6Data,
            borderColor: "#AA00AA",
            backgroundColor: "#AA00AA",
            label: "TC6",
          },
        ]
      }
      
    const config = {
        type: "line",
        data: data,
        options: {
          interaction: {
              intersect: false,
              mode: 'index',
              axis: 'x'
          },
          maintainAspectRatio: false,
          legend: {
            display: true,
          },

          //Set the rotation of the X axis labels
          scales: {
              x: {
                  ticks: {
                    maxRotation: 0,
                    minRotation: 0
                    }
              }
          }
      },
    
    }
    return config;
}


//Getting CSV and building plot
function getCSV() { 
    var url = "./OnlineLog.csv";

    var request = new XMLHttpRequest();  
    request.open("GET", url, false);   
    request.send(null);  
    
    var csvData = new Array();
    var jsonObject = request.responseText.split(/\r?\n|\r/);
    for (var i = 0; i < jsonObject.length; i++) {
      csvData.push(jsonObject[i].split('\n'));
    }
    
    //Convert CSV from string to array
    var csvFile = csvData.map(function(d) {
        return String(d).split(',');
    });
    
    return csvFile;
}


//Dark mode
document.getElementById("title").addEventListener("click", function(){
    var currBCol = document.body.style.backgroundColor;
    var newBCol = "#222";
    var newTCol = "#a2aeff";
    var newGCol = '#AAA';
    
    if (currBCol === "rgb(34, 34, 34)") {
        newBCol = "#FFF";
        newTCol = "#1D2873";
        newGCol = '#333';
    }
    document.body.style.backgroundColor = newBCol;
    document.body.style.color = newTCol;
    
    //Update the chart
    myChart.options.scales.x.grid.color = newGCol;
    myChart.options.scales.x.grid.borderColor = newGCol;
    myChart.options.scales.x.ticks.color = newGCol;
    
    myChart.options.scales.y.grid.color = newGCol;
    myChart.options.scales.y.grid.borderColor = newGCol;
    myChart.options.scales.y.ticks.color = newGCol;
    
    myChart.options.plugins.legend.labels.color = newGCol;
    myChart.update();
});



//Remake chart when it needs to reload data
function remake() {
    var newFile = getCSV();
    
    //If the file has not changed we don't need to refresh the window
    if(newFile[newFile.length-2][0] !== document.getElementById("LastRead").textContent.replace(',',' - ')) {
        myChart.destroy(); //Delete old chart
        myChart = new Chart(canvas,buildChart(getCSV())); //make new chart
    }
    
    setTimeout(remake,30000); //Refresh every 30s
}


//Build the chart
var canvas = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(canvas,buildChart(getCSV()));

remake();
