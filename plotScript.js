function makeChart(csvFile) {

  var timeLabels = csvFile.map(function(d) {
    return d.Time;
  });
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
  var tc5Data = csvFile.map(function(d) {
    return d.Temp5;
  })
  var tc6Data = csvFile.map(function(d) {
    return d.Temp6;
  })
  
  var tcHData = new Array(tc1Data.length).fill("1300"); //make the high temp array since it is not in the file
  

  var chart = new Chart('chart', {
    type: "line",
    options: {
      maintainAspectRatio: false,
      legend: {
        display: true
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
        {
          data: tc5Data,
          fill: false,
          borderColor: "#00B366",
          label: "TC5"
        },
        {
          data: tc6Data,
          fill: false,
          borderColor: "#AA00AA",
          label: "TC6"
        },
        {
          data: tcHData,
          fill: true,
          borderColor: "#450707",
          label: "HIGH",
          pointStyle: "line"
        },
      ]
    }
  });
}

// Request data using D3
d3
  .csv("./LogProgram/AllTempLogs.csv")
  .then(makeChart);
