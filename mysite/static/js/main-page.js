
function initTable()
{

    setInterval(function(){

        //summaryTable = $("#table_summary")
        $("#product_panel").bootstrapTable('refresh',{silent: true});
        $("#real_panel").bootstrapTable('refresh',{silent: true});
        // update summary statistics
//	        toSummaryData()

    },3000)

}
function productNameFormater(value){
    var color='black';

    return '<div  style="font-weight: bold; color: ' + color + ';font-size:180%">'+ value + '</div>';

 }
function returnFormater(value){
    var color;
    if(value > 0){
        color = '#f00000';
    }
    else if(value == 0){
            color = '#8a8c8d';
    }else{
        color = '#237f52';
    }
    return '<div  style="font-weight: bold;color: ' + color + ';font-size:180%"">'+ value + '</div>';

}

var django_name_list = [];
var  django_name_dict = {};


var url_path = "../static/tableData/Manage/product_account_manage.json";

$.ajaxSettings.async=false;
$.getJSON(url_path,function (data) {

    for(var i =0;i<data.length;i++){

        var account_number = data[i].account_number;
        var django_name = data[i].django_name;
        django_name_list.push([account_number,django_name]);
        django_name_dict[account_number] = django_name;
    }
 });
//console.log(django_name_dict);


function djangoNameFormater(value){


    var new_value = value;
    var account_number_origin = value.split('_')[1];
     new_value = value.split('_')[0] + '_' + django_name_dict[account_number_origin] ;

    return '<div style="font-weight: bold;font-size:180%">'+ new_value + '</div>';

}



 function productPercentReturnFormater(value){
    var color;
    if(value>0){
        color = 'red';
        value = (value * 100).toFixed(2).toString() + "%";
    }else if(value < 0 ){
        color = 'green'
        value = (value * 100).toFixed(2).toString() + "%";
    }else{
        color = '#8a8c8d'
        value = '0'
    }

    return '<div  style="font-weight: bold;font-size:180%;color: ' + color + '">'+ value + '</div>';
 }


addLoadEvent(initTable);