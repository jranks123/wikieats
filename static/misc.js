$('#goButton').hide();
console.log("helo");
$('#city_link').on('change', function (e) {
var optionSelected = $("option:selected", this);
var text = optionSelected.text();
console.log(text);
if(text == "Select City"){
console.log("helo");
$('#goButton').hide();
}else{
console.log("#helssso");
$('#goButton').show();
}
});

