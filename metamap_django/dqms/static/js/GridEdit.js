/**
 * Created by will on 15/12/8.
 */

function GetRowData(row){
    var rowData="";
    var name = row.parentNode.rows[0].cells[0].getAttribute("Name"); //只取第一列
    if(name && name != null && name !='null'){
        var value = row.cells[0].getAttribute("Value");
        if(!value){
            value = row.cells[0].innerHTML;
        }
        rowData = value;
    }
    return rowData;
}

function GetTableData(table){
    if(table.rows.length<2){
        return null;
    }
    var tableData = GetRowData(table.rows[1]); //对于数据源，只取一行
    return tableData;
}

function GetTableAllData(table){
    var tableData = new Array();
    for(var i=1; i<table.rows.length;i++){
        tableData.push(GetRowAllData(table.rows[i]));
    }
    return tableData;
}

function GetRowAllData(row){
    var rowData ="";
    for(var j=0;j<row.cells.length; j++){
        name = row.parentNode.rows[0].cells[j].getAttribute("Name");
        if(name && name != null && name !='null'){
            var value = row.cells[j].getAttribute("Value");
            if(!value){
                value = row.cells[j].innerHTML;
            }
            rowData += name+"="+value+"^";
        }
    }
    rowData = rowData.substring(0,rowData.length-1);
    return rowData;
}

