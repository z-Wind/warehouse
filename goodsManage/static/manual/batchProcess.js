//讀檔
function loadFile(input, func)
{
    if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
        alert('The File APIs are not fully supported in this browser.');
        return;
    }

    var aa = document.getElementById('callback');
    if (!input) {
        alert("Um, couldn't find the fileinput element.");
    }
    else if (!input.files) {
        alert("This browser doesn't seem to support the `files` property of file inputs.");
    }
    else if (!input.files[0]) {
        alert("Please select a file before clicking 'Load'");
    }
    else {
        //var myFiles = $('#' + id_fileinput).prop('files'); 同 input.files
        file = input.files[0];
        fr = new FileReader();
        fr.onload = function(event) {
            // The file's text will be printed here
            func(event.target.result.replace(/\n/g, "\\n"));
        };
        fr.readAsText(file, "big5");
    }
}

// 讀取檔案後處理資料
function processData(str) {

    var form = $('<form action="' + url_batch + '" method="post">' +
      '<input name='+ csrf['name'] + ' value='+ csrf['value'] + ' type="hidden">' +
      '<input type="textarea" name="file" value="' + str + '" />' +
      '</form>');
    $('body').append(form);
    form.submit();
}

$(document).ready(function() {
    // 回溯讀檔用
    $('#batchUpload').change(function(event) {
        if(confirm('將直接更改資料庫\n請務必確認資料正確性？'))
        {
        }
        else
        {
            return false
        }

        loaded = true;
        loadFile(event.target, processData);
        // for chrome on change doesn't work
        $(this).val("");
    });
});
