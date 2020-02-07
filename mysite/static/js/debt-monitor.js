
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
console.log(django_name_dict);


function djangoNameFormater(value){

    var new_value = value;
    var account_number_origin = value.split('_')[1];
    new_value = django_name_dict[account_number_origin] + '_' + value.split('_')[0];

    return '<div >'+ new_value + '</div>';

}


function initTable()
{

    summaryTable = $("#table_summary")

    summaryTable.on('click-cell.bs.table', function(e, column, value, row, $element){
        //alert( "Value: " + row);
        // load detail table according to sector name
        $("#detail-table-caption").text(row.strategy_name);
//        $("#input1").attr("value",$("#detail-table-caption")[0].innerText);
        $("#input1").attr("value",row.strategy_name);



        $("#detail_table_panel").show();
        $("#detail_table").bootstrapTable('refresh',{url: "../static/tableData/TempData/" + row.strategy_name + "_position.json"});


        var strategy_name = $("#detail-table-caption")[0].innerText;
        var order_url_path = "../refine_order/?strategy_name=" + row.strategy_name;
//        $('#order_table').bootstrapTable('refresh',{url:order_url_path});

        $.getJSON(order_url_path, function(data) {
             $('#order_table').bootstrapTable('load',data.data);
             $("#order-table-caption").text(data.length);

        });

        $("#order_table_panel").show()
        var count = 0;
        count = computeStrategySum();
        $("#security_count").text(django_name_dict[strategy_name.split("_")[1]]  + " " + row.strategy_name.split('_')[0] + "  持仓：  [ " + count + " ]");


    });

    setInterval(function(){

	        $("#detail_table").bootstrapTable('refresh',{silent: true});
	        $("#table_summary").bootstrapTable('refresh',{silent: true});
	        toSummaryData();
    },3000)


    setInterval(function(){
//	        $("#order_table").bootstrapTable('refresh',{silent: true});
	        var web_length = $("#order-table-caption")[0].innerText;
            var strategy_name = $("#detail-table-caption")[0].innerText;
            var url_path = "../newOrderApi/?strategy_name=" + strategy_name + "&old_len=" + web_length;

            addNewOrder(url_path);
	        //getNewOrder();
    },6000)

}

function computeStrategySum(){

    StrategyPositionTable = $("#detail_table").bootstrapTable('getData');
    var security_amount = 0;

    for(var i = 0;i<StrategyPositionTable.length;i++){
        if (StrategyPositionTable[i].market_value != 0){
            security_amount = security_amount + 1;
        }
    }

    $("#security_count").attr("value",security_amount);

    return security_amount;
}



function addNewOrder(url_path){

    $.getJSON(url_path,function (data) {

        var msg = "";

        $("#order-table-caption").text(data.new_len);

//        console.log(url_path);
//        console.log(data);
//        console.log(exist_order_ids);

        var priority = {"拒绝":5,"已成":4,"已撤单":3,"部分成交":2,"未成交":1,"OK":0}

        var counts = 0;
        for (j=0;j<data.data.length;j++){
//        如果订单状态不在我们的列表里，则默认筛掉
            if(Object.keys(priority).indexOf(data.data[j].entrust_status) == -1){
                continue
            }

            if(data.data[j].entrust_status == '已成'){
                if (data.data[j].open_close == '开仓'){
                    var msg1 = '触发' + data.data[j].stock_name.split('_')[0];
                    msg += msg1;
                }
            }

            var web_data = $("#order_table").bootstrapTable('getData');
            var web_length = web_data.length;
//            console.log("web_length:");
//            console.log(web_length);
            var new_length = data.new_len;
            var exist_order_ids = [];
            var new_order_id = data.data[j].system_order_id;

            // 遍历一遍，找到所有的system_order_id,为了减少时间，遍历到当前id即停止
            var counts = -1;
            var web_index = -1;
            for (i=0;i<web_length;i++){
                counts += 1;
                if (new_order_id == web_data[i].system_order_id){
                    var web_index = counts;
                    break;
                }
//                exist_order_ids.push(web_data[i].system_order_id);
            }

//            var web_index = exist_order_ids.indexOf(data.data[j].system_order_id);

            if (web_index != -1){
                 var new_status = data.data[j].entrust_status;
                 var old_status = web_data[web_index].entrust_status;

                 if (priority[new_status] > priority[old_status]){
                     $('#order_table').bootstrapTable('updateRow', {
                            index: web_index,
                            replace:true,
                            row: data.data[j]
                     });
//                     console.log("订单状态更新");
//                     console.log("system_order_id:",exist_order_ids[web_index]);
//                     console.log(web_index);
//                     console.log('old_status:',old_status);
//                     console.log('new_status:',new_status);

                 }else{
                    console.log(new_status);
                    console.log(old_status);
                    console.log("Not OK");
                 }

            }
            else{
                $("#order_table").bootstrapTable('insertRow',
                    {
                        index:0,
                        row:data.data[j]

                    });
//                    console.log("新订单添加");
//                    console.log(data.data[j]);
//                    counts += 1;


            }
        }

        sayOrder(msg);
        console.log(msg);


    });

}

function select_show_strategy(){

        //设置需要显示的列
        var columns = [{
           field:"strategy_name",
          title: '策略名'
        }, {
            field: 'capital',
            title: '总资产'
        } , {
            field: 'market_value',
            title: '持仓市值'
        } ,  {
            field: 'PNL',
            title: '盈亏'
        } ];

        //需要显示的数据
        var html_title = document.title;
        console.log(html_title);
        var url_path = "../static/tableData/TempData/"+html_title+"_group_pnl.json";
        $.getJSON(url_path,function (data) {

            var select_data = [];
            for(var j=0;j<data.length;j++){
                var show = data[j].show;
                if(show == "1"){
                    select_data.push(data[j]);
                }
            }
        console.log(select_data);

        //bootstrap table初始化数据
        $('#table_summary').bootstrapTable({
            columns: columns,
            data: select_data,
            silent: true
        });
        });

}

function initOrderNum(test_row){

    var url_path = "../static/tableData/TempData/" + test_row + "_order.json";

    $.getJSON(url_path,function (data) {


        var orderData = data;
        for(var i = 0; i < orderData.length;i++){
            if(orderData[i].entrust_status == '已成' || orderData[i].entrust_status == '拒绝'){
                if(order_id_list.indexOf(orderData[i].system_order_id) == -1){
                    order_id_list.push(orderData[i].system_order_id);
                }
            }
        }
//        console.log(order_id_list);

    });
}

function getNewOrder(){

//    console.log($("#detail-table-caption")[0].innerText)
    var url_path = "../static/tableData/TempData/" + $("#detail-table-caption")[0].innerText + "_order.json";

    $.getJSON(url_path,function (data) {

        var orderData = data;
        var msg = '';
        for(var i = 0; i < orderData.length;i++){
            if(orderData[i].entrust_status == '已成'){
                if(order_id_list.indexOf(orderData[i].system_order_id) == -1){
                    order_id_list.push(orderData[i].system_order_id);

                    var msg1 = orderData[i].long_short + ' ' + orderData[i].stock_name.split('_')[0];
                    msg += msg1;
                }
            }
            if(orderData[i].entrust_status == '拒绝' || orderData[i].business_price == '拒绝'){
                if(order_id_list.indexOf(orderData[i].system_order_id) == -1){
                    order_id_list.push(orderData[i].system_order_id);
                    var msg1 = orderData[i].stock_name.split('_')[0] + '拒绝';
                    msg += msg1;
                }
            }

        }
        sayOrder(msg);
//        test_msg = '凯龙转债_123456'
//        console.log(test_msg.split('_')[0]);
    });
}

function sayOrder(m) {
  var msg = new SpeechSynthesisUtterance();
  var voices = window.speechSynthesis.getVoices();
  msg.volume = 10;
  msg.rate = 1.5;
  msg.text = m;
  speechSynthesis.speak(msg);
}

function toSummaryData(){

    StrategySummaryData = $("#table_summary").bootstrapTable('getData');

    trade_pnl_temp = 0;
    pos_pnl_temp = 0;
    market_value_temp = 0;
    accum_pnl_temp = 0;
    capital = 0;
    PNL_temp = 0


    for(var i = 0; i < StrategySummaryData.length;i++){

        market_value_temp += parseFloat(StrategySummaryData[i].market_value);
        PNL_temp += parseFloat(StrategySummaryData[i].PNL);
        accum_pnl_temp += parseFloat(StrategySummaryData[i].accum_pnl);
    }

    updateSummary('accum_pnl', accum_pnl_temp);
    updateSummary('total_pnl', PNL_temp);
    updateCapital('market_value',market_value_temp);

}
//
//function sayOrder(m) {
//    var msg = new SpeechSynthesisUtterance();
//    var voices = window.speechSynthesis.getVoices();
//    msg.volume = 10;
//    msg.rate = 2;
//    msg.text = m;
//    speechSynthesis.speak(msg);
//}

function updateCapital(divID,number){

    $('#'+divID).text(number.toFixed(2));
    if(number>0){
            $('#'+divID).css({'color':'dark','font-size': '150%'});
        }else{
             $('#'+divID).css({'color':'gray','font-size': '150%'});
    }
}

function updateSummary(divID,number){

    $('#'+divID).text(number.toFixed(2));
        if(number>0){
            $('#'+divID).css({'color':'red','font-size': '150%'});
        }else if(number == 0){
            $('#'+divID).css({'color':'#8a8c8d','font-size': '150%'});
        }
        else{
             $('#'+divID).css({'color':'green','font-size': '150%'});
        }
}

function UpdateStrategySummaey(divID,number){

    $('#'+divID).text(number.toFixed(2));
        if(number>0){
            $('#'+divID).css({'color':'red','font-size': '100%'});
        }else if(number == 0){
            $('#'+divID).css({'color':'#8a8c8d','font-size': '100%'});
        }
        else{
             $('#'+divID).css({'color':'green','font-size': '100%'});
        }
}

function updateCost(divID,number){

    $('#'+divID).text(number.toFixed(2));
    $('#'+divID).css({'color':'black','font-size': '200%'});

}


addLoadEvent(initTable);