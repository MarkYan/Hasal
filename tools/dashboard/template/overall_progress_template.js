var GAUGE_MACHINE_VAR = {

chart: {
  type: 'solidgauge',
    backgroundColor: '#1a1a1a',
},

title: null,

pane: {
  center: ['50%', '85%'],
  size: '140%',
  startAngle: -90,
  endAngle: 90,
  background: {
    backgroundColor:'#1a1a1a',
    innerRadius: '60%',
    outerRadius: '100%',
    shape: 'arc'
  }
},

tooltip: {
  enabled: false
},

// the value axis
yAxis: {
  stops: [
    [0.1, '#ff0000'], // red
    [0.5, '#ffff00'], // yellow
    [0.9, '#00ff00']  // green
  ],
  lineWidth: 0,
  minorTickInterval: null,
  tickAmount: 0,
  tickPixelInterval: 0,
  title: {
    y: -70,
    text: '{{MACHINE}}', //code add here
      style: {'font-size':'19px', 'color':'#666666'}
  },
  labels: {
      enabled: false
  },
  min: 0,
  max: 100,
  tickInterval: 0.01,
  tickWidth: 0
},

plotOptions: {
  solidgauge: {
    dataLabels: {
      y: 5,
      borderWidth: 0,
      useHTML: true
    }
  }
},
credits: {
  enabled: false
},
  series: [{
  name: '{{MACHINE}}', //code add here
  data: '{{PERCENTAGE}}', // code add here
  dataLabels: {
    format: '<div style="text-align:center"><span style="font-size:25px;color:' +
      ((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">{y}%</span><br/>' +
      '<span style="font-size:12px;color:silver"></span></div>'
  },
  tooltip: {
    valueSuffix: ''
  }
}]
};