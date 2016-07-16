//inputForm.html
//將選到的值填入左邊表格
function changeSel(dataList, idchange, idlist, idsel, selThis)
{
    document.getElementById(idchange).value = selThis.options[selThis.selectedIndex].text;
    changeList(dataList, idlist, idsel, document.getElementById(idchange).value.toLowerCase());
}

//測試
function myFunction()
{
    var x = document.getElementById("id_good_type");
    x.value = x.value.toUpperCase();
}

//改變列表內容
function changeList(dataList, idlist, idsel, text, text2)
{
    text2 = (typeof text2 === 'undefined') ? '*' : text2;
    if(text.length == 0)
    {
        document.getElementById(idlist).style.visibility = "hidden";
        return;
    }
    document.getElementById(idlist).style.visibility = "visible";

    var showlist = [];
    for(var i=0; i<dataList.length; i++)
    {
        if((((dataList[i].toLowerCase().indexOf(text) != -1 && text != "") || text == "*"))
        && (((dataList[i].toLowerCase().indexOf(text2) != -1 && text2 != "") || text2 == "*")))
        {
            showlist.push(dataList[i]);
        }
    }

    document.getElementById(idsel).disabled = false;
    if(showlist.length == 0)
    {
        showlist.push("無此選項");
        document.getElementById(idsel).disabled = true;
    }

    for(var i=0; i<showlist.length; i++)
    {
        document.getElementById(idsel).options[i] = new Option(showlist[i], showlist[i]);	// 設定新選項
    }

    document.getElementById(idsel).length = showlist.length;	// 刪除多餘的選項

    if(showlist.length == 1 && showlist[0].toLowerCase() == text)
    {
        document.getElementById(idlist).style.visibility = "hidden";
    }
}

//改變選單內容
function changeDownList(datalist, idsel, text)
{
    var showlist = [];
    for(var i=0; i<datalist.length; i++)
    {
        if((datalist[i].toLowerCase().indexOf(text) != -1 && text != "") || text == "*")
        {
            showlist.push(datalist[i]);
        }
    }

    for(var i=0; i<showlist.length; i++)
    {
        document.getElementById(idsel).options[i] = new Option(showlist[i], showlist[i]);	// 設定新選項
    }

    document.getElementById(idsel).length = showlist.length;	// 刪除多餘的選項
}

function doubleCheck()
{
    var dataArray = $("#id_input_form").serializeArray();
    var str = ""

    for(var i=0; i<dataArray.length; i++)
    {
        if(dataArray[i].name === "csrfmiddlewaretoken" || dataArray[i].name === "ok" || dataArray[i].name === 'initial-date' || dataArray[i].name === 'initial-datetime')
            continue
        else
        {
            if($("#id_" + dataArray[i].name).is("select"))
                str = str + $("#id_" + dataArray[i].name + " option:selected").text() + "\n";
            else
                str = str + dataArray[i].value + "\n";
        }
    }

    if(confirm(str + '\n是否確認送出？'))
    {
        return true
    }
    else
    {
        return false
    }
}

//overview.html
//畫推疊圖
function plotStack(plot_id, dataW1, dataW2, ticks)
{
    var dataset = [
        { label: "遺失率", data: dataW1, color: "red" },
        { label: "報廢率", data: dataW2, color: "blue" }
    ];

    var stack = 0,
        bars = true,
        lines = false,
        steps = false;

    var options = {
        series: {
            stack: stack,
            lines: {
                show: lines,
                fill: true,
                steps: steps
            },
            bars: {
                show: bars,
                align: "center",
                barWidth: 0.6
            }
        },
        xaxis: {
            ticks: ticks,
        },
        yaxis: {
            axisLabel: "耗損率",
            axisLabelUseCanvas: true,
            axisLabelFontSizePixels: 14,
            axisLabelFontFamily: '新細明體, Arial',
            axisLabelPadding: 5,
            tickFormatter: function (v, axis) {
                v = Math.round(v * 100) / 100
                return v + "%";
            }
        },
        grid: {
            hoverable: true,
            borderWidth: 2,
            backgroundColor: { colors: ["#ffffff", "#EDF5FF"] }
        }
    };
    $.plot($(plot_id), dataset, options);
}

//圖表加上 tooltip
var previousPoint = null, previousLabel = null;

$.fn.UseTooltip = function ()
{
    $(this).bind("plothover", function (event, pos, item)
    {
        if (item)
        {
            if ((previousLabel != item.series.label) || (previousPoint != item.dataIndex))
            {
                previousPoint = item.dataIndex;
                previousLabel = item.series.label;
                $("#tooltip").remove();

                var y = Math.round((item.datapoint[1] - item.datapoint[2])*100)/100;

                var color = item.series.color;

                //console.log(item.datapoint);

                showTooltip(item.pageX,
                item.pageY,
                color,
                "<strong>" + item.series.label + "</strong><br>" + item.series.xaxis.ticks[item.dataIndex].label + " : <strong>" + y + "</strong> %");
            }
        }
        else
        {
            $("#tooltip").remove();
            previousPoint = null;
        }
    });
};

function showTooltip(x, y, color, contents)
{
    $('<div id="tooltip">' + contents + '</div>').css({
        position: 'absolute',
        display: 'none',
        top: y - 40,
        left: x - 120,
        border: '2px solid ' + color,
        padding: '3px',
        'font-size': '9px',
        'border-radius': '5px',
        'background-color': '#fff',
        'font-family': 'Verdana, Arial, Helvetica, Tahoma, sans-serif',
        opacity: 0.9
    }).appendTo("body").fadeIn(200);
}

function inventorySearch(id_type, link)
{
    var type = $("#" + id_type).val();
    window.open(link + '&type=' + type , '_blank');
}

function appendURL(param, paramVal)
{
    var s = window.location.search.replace('&ok=yes&inquiry=查詢', "").replace(/page=\d+/, "");
    var h = window.location.hash;
    var now_url = window.location.origin + window.location.pathname;
    var new_url = updateURLParameter(now_url + s, param, paramVal);
    window.location.assign(new_url + h);
}

function updateURLParameter(url, param, paramVal){
    var newAdditionalURL = "";
    var tempArray = url.split("?");
    var baseURL = tempArray[0];
    var additionalURL = tempArray[1];
    var temp = "";
    if (additionalURL) {
        tempArray = additionalURL.split("&");
        for (i=0; i<tempArray.length; i++){
            if(tempArray[i].split('=')[0] != param){
                newAdditionalURL += temp + tempArray[i];
                temp = "&";
            }
        }
    }

    var rows_txt = temp + "" + param + "=" + paramVal;
    return baseURL + "?" + newAdditionalURL + rows_txt + '&ok=yes&inquiry=查詢';
}

$(document).ready(function(){
    $("div.fold").click(function()
    {
        if( $(this).text() == "+")
        {
            $(this).text("-");
        }
        else
        {
            $(this).text("+");
        }
        $(this).parent().children("div.fold+div").slideToggle();
    });
});
