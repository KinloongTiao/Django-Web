function backColor(){
    strategy_all_panel = $("#strategy_all_panel")



    strategy_all_panel.on('click-row.bs.table', function (e, row, $element) {
        $($element).siblings().removeClass('warning');
        $($element).addClass('warning');
        $('.success').css("background-color","#ffffff");
    });

}

function initTable()
{

    product_panel = $("#product_panel")
    product_account_panel = $("#product_account_panel")
    strategy_all_panel = $("#strategy_all_panel")


    strategy_all_panel.on('click-cell.bs.table', function(e, column,value, row, $element){


        $("#strategy_change_input1").attr("value",row.strategy_name);

        $("#strategy_input1").attr("value",row.strategy_name);
        $("#strategy_input2").attr("value",row.account_number);
        $("#strategy_input7").attr("value",row.capital);
        $("#strategy_input6").attr("value",row.strategy_type);
        $("#strategy_input3").attr("value",row.group);
        $("#strategy_input5").attr("value",row.real_or_simulate);
        $("#strategy_input4").attr("value",row.show);
        $("#strategy_input10").attr("value",row.strategy_class);
        $("#strategy_input11").attr("value",row.total_asset);



    });

    product_panel.on('click-cell.bs.table', function(e, column, value, row, $element){

        $("#product_input1").attr("value",row.account);
        $("#product_input11").attr("value",row.account);

        $("#product_input2").attr("value",row.total_asset);
        $("#product_input3").attr("value",row.show);
        $("#product_input4").attr("value","0");


    });
    product_account_panel.on('click-cell.bs.table', function(e,column, value, row, $element){

        $("#account_input1").attr("value",row.product_name);
        $("#account_input2").attr("value",row.account_number);
        $("#account_input3").attr("value",row.django_name);



    });


    setInterval(function(){

        $("#product_account_panel").bootstrapTable('refresh',{silent: true});
        $("#product_panel").bootstrapTable('refresh',{silent: true});
        $("#strategy_all_panel").bootstrapTable('refresh',{silent: true});


    },3000)

}


addLoadEvent(initTable);
addLoadEvent(backColor);