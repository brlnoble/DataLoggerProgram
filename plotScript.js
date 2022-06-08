function makeChart(csvFile) {

  //Get the time column
  var timeLabels = csvFile.map(function(d) {
      return d.Time;
      });


  //If the file has not changed we don't need to refresh the window
  console.log(timeLabels[timeLabels.length-1]);
  console.log(document.getElementById("LastRead").textContent);
  if(timeLabels[timeLabels.length-1] === document.getElementById("LastRead").textContent) {
    return;
  };

  //Put the date and time on two lines for the graph
  timeLabels = timeLabels.map(function(t) { 
      return t.split(' - '); 
      }); 
  
  //Get all the TC columns
  var tc1Data = csvFile.map(function(d) {
    return d.Temp1;
  });
  var tc2Data = csvFile.map(function(d) {
    return d.Temp2;
  })
  var tc3Data = csvFile.map(function(d) {
    return d.Temp3;
  })
  var tc4Data = csvFile.map(function(d) {
    return d.Temp4;
  })
 /* var tc5Data = csvFile.map(function(d) {
    return d.Temp5;
  }) */
  var tc6Data = csvFile.map(function(d) {
    return d.Temp6;
  })
  
  //Create an array for the high temperature warning
  var tcHData = new Array(tc1Data.length).fill("1300");
  
  //Update the numeric text at the top of the screen
  document.getElementById("TC1").textContent=tc1Data[tc1Data.length-1];
  document.getElementById("TC2").textContent=tc2Data[tc2Data.length-1];
  document.getElementById("TC3").textContent=tc3Data[tc3Data.length-1];
  document.getElementById("TC4").textContent=tc4Data[tc4Data.length-1];
  //document.getElementById("TC5").textContent=tc5Data[tc5Data.length-1];
  document.getElementById("TC6").textContent=tc6Data[tc6Data.length-1];
  document.getElementById("LastRead").textContent=timeLabels[timeLabels.length-1];
  
  
  var chart = new Chart('chart', {
    type: "line",
    options: {
      maintainAspectRatio: false,
      legend: {
        display: true
      },

      //Set the rotation of the X axis labels
      scales: {
            xAxes: [{
                ticks: {
                    maxRotation: 0,
                    minRotation: 0
                }
            }]
        }
    },

    data: {
      labels: timeLabels,
      datasets: [
        {
          data: tc1Data,
          fill: false,
          borderColor: "#FF0000",
          label: "TC1"
        },
        {
          data: tc2Data,
          fill: false,
          borderColor: "#FFAA00",
          label: "TC2"
        },
        {
          data: tc3Data,
          fill: false,
          borderColor: "#365BB0",
          label: "TC3"
        },
        {
          data: tc4Data,
          fill: false,
          borderColor: "#444",
          label: "TC4"
        },
        /*{
          data: tc5Data,
          fill: false,
          borderColor: "#00B366",
          label: "TC5"
        },*/
        {
          data: tc6Data,
          fill: false,
          borderColor: "#AA00AA",
          label: "TC6"
        },
        {
          data: tcHData,
          fill: true,
          borderColor: "#00B366",
          label: "HIGH",
          pointStyle: "line"
        },
      ]
    }
  });
  
}

// Request data using D3
function getCSV() { 
  d3
    .csv("./OnlineLog.csv?" + new Date().getTime())
    .then(makeChart);

  //Run the program every 60s
  setTimeout(getCSV, 60000);
}

//Initial call
getCSV();
