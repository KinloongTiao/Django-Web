
// initialize table for each MOM strategy
// refresh table for each MOM strategy
var total_trade_pnl = 0;
var total_pos_pnl = 0;
var total_MOM_pnl = 0;
var total_pnl = 0;
var hedge_trade_pnl = 0;
var hedge_pos_pnl = 0;
var hedge_total_pnl = 0;
var tradingCost = 0;

var total_market_value = 0;
var totalCapital = 0;
var totalCapital_nomial = 0;

var tableList=[]
var dataUrlList = []

function initTable()
{

    summaryTable = $("#table_summary")
    //console.log($("#table_summary"))
    summaryTable.on('click-cell.bs.table', function(e, value, row, $element){
        //alert( "Value: " + row);
        // load detail table according to sector name
        $("#detail-table-caption").text(row)
        $("#detail_table_panel").show()
        $("#detail_table").bootstrapTable('refresh',{url: "../static/tableData/" + row + ".json"});

        $("#order-table-caption").text(row)
        $("#order_table_panel").show()
        $("#order_table").bootstrapTable('refresh',{url: "../static/tableData/" + row + "_order.json"});
    });

    setInterval(function(){
		$.get('/GetStrategyList/',true, function(data) {
	        // refresh table for MOM summary (this table will always exist)
	        //$("#table_portfolio").bootstrapTable('refresh',{silent: true});
	        
	        //summaryTable = $("#table_summary")
	        $("#detail_table").bootstrapTable('refresh',{silent: true});
	        $("#order_table").bootstrapTable('refresh',{silent: true});
	        $("#table_summary").bootstrapTable('refresh',{silent: true});
	        // update summary statistics
	        toSummaryData()
	      });
    },1000)

}

function toSummaryData(){
    MOMSummaryData = $("#table_summary").bootstrapTable('getData');
    //console.log(MOMSummaryData)
    trade_pnl_temp = 0;
    pos_pnl_temp = 0;
    pnl_temp = 0;
    tradingCost_temp = 0;


    for(var i = 0; i < MOMSummaryData.length;i++){
        //console.log(MOMSummaryData[i]);
        trade_pnl_temp += parseFloat(MOMSummaryData[i].close_profit);
        pos_pnl_temp += parseFloat(MOMSummaryData[i].position_profit);
        tradingCost_temp += parseFloat(MOMSummaryData[i].fee);
    }

    //console.log(trade_pnl_temp + " " + pos_pnl_temp + " " + market_value_temp)
    total_trade_pnl = trade_pnl_temp;
    //console.log(total_trade_pnl);
    total_pos_pnl = pos_pnl_temp;
    //console.log(total_pos_pnl);
    tradingCost = tradingCost_temp
    total_pnl = total_trade_pnl + total_pos_pnl - tradingCost_temp;
    

    // update field
    updateSummary('trade_pnl', total_trade_pnl);
    updateSummary('pos_pnl', total_pos_pnl);
    updateCost('trade_cost', tradingCost);
    updateSummary('total_pnl', total_pnl);

}

function updateCapital(divID,number){

    $('#'+divID).text(number.toFixed(2));
    if(total_market_value>0){
            $('#'+divID).css({'color':'#514b78','font-size': '200%'});
        }else{
             $('#'+divID).css({'color':'green','font-size': '200%'});
    }
}

function updateSummary(divID,number){

    $('#'+divID).text(number.toFixed(2));
        if(number>0){
            $('#'+divID).css({'color':'red','font-size': '200%'});
        }else if(number == 0){
            $('#'+divID).css({'color':'#8a8c8d','font-size': '200%'});
        }
        else{
             $('#'+divID).css({'color':'green','font-size': '200%'});
        }
}

function updateCost(divID,number){

    $('#'+divID).text(number.toFixed(2));
    $('#'+divID).css({'color':'black','font-size': '200%'});

}

function allowTradeStyle(value, row, index){

    // not trade
    if(value == 1){
        return{
            classes: 'default'
        };
    }else if(value == 0){
        return{
            classes: 'danger'
        };
    }

    return {};
}

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
    return '<div  style="font-weight: bold;color: ' + color + '">'+ value + '</div>';

}


addLoadEvent(initTable);