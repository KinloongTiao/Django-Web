

function restrictStyle(value, row, index){

    // not trade
    if(value == 0){
        return{
            classes: 'default'
        };
    }else if(value == 1){
        return{
            classes: 'danger'
        };
    }

    return {};
}

function MPUpdatedStyle(value, row, index){

    // not trade
    if(value == 1){
        return{
            classes: 'success'
        };
    }else if(value == 0){
        return{
            classes: 'danger'
        };
    }

    return {};
}

function positionStyle(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];
    if(value>0){
        return{
            classes: classes[3],
        };
    }else{
        return{
            classes: classes[0]
        };
    }
    return {};
}

function tradingSchemeStyle(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];
    if(value == 1){
        return{
            classes: classes[1],
        };
    }else if(value == 2){
        return{
            classes: classes[2]
        };
    }else{
        return{
            classes: classes[4]
        };
    }
    return {};
}

function positionStyle_SS(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];
    if(value>0){
        return{
            classes: classes[3],
        };
    }
    else if(value ==0){
        return{
            classes: classes[0]
        };
    }else{
        return{
            classes: classes[1]
        };
    }
    return {};
}

function entryStyle(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];
    if(value == 0){
        return{
            classes: classes[0],
        };
    }else if(value == 1){
        return{
            classes: classes[2]
        };
    }else if(value < 1){
        return{
            classes: classes[1]
        };
    }else if(value > 1){
        return{
            classes: classes[4]
        };
    }
    return {};
}

function marginRatioStyle(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];
    if(value <= 1.5){
        return{
            classes: classes[3]
        };
    }else if(value > 1.5 && value <= 2){
        return{
            classes: classes[2]
        };
    }
    else if(value > 2){
        return{
            classes: classes[1]
        };
    }
    return {};
}

function netMVStyle(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];
    if(value > 0){
        return{
            classes: classes[4]
        };
    }else if(value < 0){
        return{
            classes: classes[1]
        };
    }else if(value == 0){
        return{
            classes: classes[0]
        };
    }

    return {};
}

function quotaStyle(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];
    if(value>0){
        return{
            classes: classes[2],
        };
    }else{
        return{
            classes: classes[4]
        };
    }
    return {};
}

function signalStyle(value, row, index) {
    var classes = ['active', 'success', 'info', 'warning', 'danger'];

    return {classes: classes[0],};
}


function signalFormater(value){
    var color;
    if(value > 0){
        color = '#f00000';
    }
    else if(value == 0){
            color = '#8a8c8d';
    }else{
        color = '#237f52';
    }
    return '<div  style="color: ' + color + '">'+ value + '</div>';

}

function oredrStateFormater(value){
    var color;
    if(value == '已成'){
        color = 'green';
    }
    else if(value == "未成交"){
            color = 'blue';
    }
    else if(value == "已撤单"){
            color = '#337AB7';
    }else{
        color = '#237f52';
    }
    return '<div  style="color: ' + color + '">'+ value + '</div>';

}

function longShortFormater(value){
    var color;
    if(value == '卖出'){

        color = 'green';
    }
    else if(value == "买入"){
            color = 'red';
    }else{
        color = '#237f52';
    }
    return '<div  style="color: ' + color + '">'+ value + '</div>';

}


function duoKongFormater(value){
    var color;
    if(value == 0){
        color = 'red';
        value = '多';
    }
    else if(value == 1){
            color = 'green';
            value = '空';
    }else{
        color = '#237f52';
        value = ' '
    }
    return '<div  style="color: ' + color + '">'+ value + '</div>';

}

function openCloseFormater(value){
    var color;
    if(value == '平仓'){
        color = 'green';
    }
    else if(value == "开仓"){
            color = 'red';
    }else{
        color = '#237f52';
    }
    return '<div  style="color: ' + color + '">'+ value + '</div>';

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
    return '<div  style="font-weight: bold; color: ' + color + '">'+ value + '</div>';

}


function productNameFormater(value){
    var color='#237f52';

    return '<div  style="font-weight: bold; color: ' + color + '">'+ value + '</div>';

 }


function fixedNumber(value){
    if (isNaN(value)){
        return value;
    }else{
        var changed_value = parseFloat(value).toFixed(2);
        return changed_value;
    }

}
String.prototype.replaceAll  = function(s1,s2){
    return this.replace(new RegExp(s1,"gm"),s2);
}

function formatFixedNumber(value){
    if (isNaN(value)){
        return value;
    }else{
        var changed_value = parseFloat(value).toFixed(2);
        return changed_value;
    }

}


 function sortNumber(value,row,index){
    return index + 1;
 }




function percentReturnFormater(value){
    var color;
    if(value=='inf%'){
        color = '#8a8c8d';
        value = 'Nan'
    }else{
        var rep_value = value.toString().replace("%","");
        var str = rep_value/100;
        var num_value = str;

        if(num_value > 0){
            color = '#f00000';
        }else if(num_value == 0){
            color = '#8a8c8d';
        }else{
            color = '#237f52';
        }
    }
    return '<div  style="font-weight: bold; color: ' + color + '">'+ value + '</div>';

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

    return '<div >'+ new_value + '</div>';

}



