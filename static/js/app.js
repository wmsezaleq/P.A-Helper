
function clearTable()
{
    $("#tabla tr").remove();
    $("#tabla").append("<tr><th>Posicion</th><th>Cantidad de MELIs registrados</th><th>% libre</th></tr>");
}



function update(calle, meli, p3)
{
    $("#picker_calle").text(calle);
    var color = "";
    if (p3 > 80)
    color = "#ADFF2F";
    else if (p3 <= 80  && p3 > 60)
    color = "#FFFF00";
    else if (p3 <= 60 && p3 > 30)
    color = "#FFD700";
    else if (p3 <= 30)
    color = "#FF6347";
    $("#picker_meli").text("[" + meli + "]");
    $("#picker_meli").css("background-color", color);
}

/* Set the width of the sidebar to 250px and the left margin of the page content to 250px */
function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

/* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}
$(function(){

    $("#filtrado_melis").hide();
    $("#filtrado_altura").hide();
    
    const socketio = io();
    var data = []; 
    var contador = 0;
    $("#picker").hide();
    var reportes = document.getElementById("reportes");
    var filtrado = document.getElementById("filtrado_modal");

    var modalOk = document.getElementById("modalOk")
    // When the user clicks on <span> (x), close the reportes
    $(".close").click(function(){
    reportes.style.display = "none";
    filtrado.style.display = "none"
    });
    var QR = true;

    function restockTable(p1, p2, p3){
        var color = "";
        if (p3 > 80)
        color = "#ADFF2F";
        else if (p3 <= 80  && p3 > 60)
        color = "#FFFF00";
        else if (p3 <= 60 && p3 > 30)
        color = "#FFD700";
        else if (p3 <= 30 && p3>=0)
        color = "#FF6347";
        else
        {
            p3 = "Saturado";
            color = "#FF6347";

        }
        

        $("#tabla").append('<tr><td style="cursor:pointer;" id="' + p1 +'">' + p1 + "</td><td>" + p2 + '</td><td style="background-color:' + color + ';">' + p3 + "</td></tr>");
        $("#" + p1).click(function(){
        pos = $(this).attr("id");
        $("#modaltitle").text(pos);
        reportes.style.display = "block";
        });
    }

    // When the user clicks anywhere outside of the reportes, close it
    window.onclick = function(event) {
        if (event.target == reportes) {
            reportes.style.display = "none";
        }

        if (event.target == modalOk) {
            modalOk.style.display = "none";
        }

        if (event.target == filtrado) {
            filtrado.style.display = "none";
        }
    }
    // Eventos

    $(document).on("click", "#report", function(){
        $("#modaltitle").text($("#picker_calle").text());
        reportes.style.display = "block";
    });
    $("#report_qr").click(function(){

        modalOk.style.display = "block";
        QR = true;
    });

    $("#report_problem").click(function(){

        modalOk.style.display = "block";
        QR = false;
    });

    $("#ok").click(function(){
        if (QR)
            socketio.emit("reporte-qr", $("#modaltitle").text());
        else
            socketio.emit("reporte-er", $("#modaltitle").text());
        modalOk.style.display = "none";
        reportes.style.display = "none";
    });

    $("#cancel").click(function(){
        modalOk.style.display = "none";
    });

    
    $("#tipo_filtrado").change(function()
    {
        switch($(this).children("option:selected").val())
        {
            case "Cantidad de MELIs":
                {
                    $("#filtrado_melis").show();
                    $("#filtrado_altura").hide();
                    break;
                }
            case "Altura":
                {
                    $("#filtrado_altura").show();
                    $("#filtrado_melis").hide();
                    break;
                }
            default:
                {
                    $("#filtrado_altura").hide();
                    $("#filtrado_melis").hide();
                }
        }
    });

    $("#accept_filter").click(function()
    {
        data.sort();
        switch($("#tipo_filtrado").children("option:selected").val())
        {
            case "Cantidad de MELIs":
            {
                clearTable();
                if ($("#type_melis").children("option:selected").val() == "Menor a")
                {
                    for(var i in data)
                    {
                        var index = data[i];
                        if (index[1] < parseInt($("#numero_melis").val()))
                        {
                            restockTable(index[0], index[1], index[2]);
                        }
                    }
                }
                else
                {
                    for(var i in data)
                    {
                        var index = data[i];
                        if (index[1] > parseInt($("#numero_melis").val()))
                        {
                            restockTable(index[0], index[1], index[2]);
                        }
                    }
                }
                break;
            }
            case "Altura":
            {
                clearTable();
                for(var i in data)
                {
                    var index = data[i]
                    if (parseInt(index[0].substring(13, 15)) == parseInt($("#numero_altura").val()))
                    {
                        restockTable(index[0], index[1], index[2]);
                    }
                }    
                break;
            }
            default:
            {
                clearTable();
                for(var i in data)
                {
                    var index = data[i];
                    restockTable(index[0], index[1], index[2]);
                }   
                break;
            }
        }
        filtrado.style.display = "none";
        closeNav();
    });
    $(document).on('click','#sort_asc', function(){
        data.sort();
        closeNav();
        clearTable();
        for (const index of data)
        {
            restockTable(index[0], index[1], index[2]);
        }

    });
    $(document).on('click','#pedir_data', function(){
        var sector = $("#sector").children("option:selected").val();
        var calle = $("#calle").children("option:selected").val();
        var piso = "";
        if (sector == "MZ")
        {
            piso = $("#piso").children("option:selected").val();
            console.log("Enviando piso " + piso + " calle " + calle + " en MZ");
        }
        else if (sector == "RK")
        {
            piso = "0";
            console.log("Enviando calle " + calle + " en RK");
        }
        else if (sector == "RO")
        {
            piso = "0";
            calle = "1";
        }
        socketio.emit('pedir', [sector, piso, calle]);
        clearTable();
        $("#msg").text(" ");
        $("#picker_calle").text("");
        $("#picker_meli").text("");
        data = [];
    });

    Array.prototype.insert = function ( index, item ) {
        this.splice( index, 0, item );
    };

    var modo = false;
    $("#filtrar").click(function()
    {
        filtrado.style.display ="block";
    });
    $("#modo").click(function(){
        if (!modo)
        {
            $("#tabla").hide();
            $("#picker").show();
            $("#modo").text("Vista en Tabla");
            closeNav();
            modo = true;
        }
        else
        {
            $("#tabla").show();
            $("#picker").hide();
            $("#modo").text("Vista en Honeywell");
            closeNav();
            modo = false;
        }
    });
   
    $("#piso").change(function(){
        if ($("#sector").val() == "MZ")
        {
            $("#calle").empty();
            if ($(this).val() == "0" || $(this).val() == "1")
            {
                for(var i = 1; i < 26; i++)
                    $("#calle").append("<option value='" + i + "'>" + i + "</option>");
    
            }
            else{
                for(var i = 1; i < 27; i++)
                    $("#calle").append("<option value='" + i + "'>" + i + "</option>");
            }
        }
    });
    $("#sector").change(function(){
        var sector = $("#sector").children("option:selected").val();
        if (sector == "RK")
        {
            $("#lpiso").hide();
            $("#lcalle").show();
            $("#calle").empty();
            $("#main").text("Ingrese la calle para iniciar la busqueda")
            for(var i = 2; i < 18; i++)
                $("#calle").append("<option value='" + i + "'>" + i + "</option>");
        }
        else if(sector ==  "MZ")
        {
            $("#lpiso").show();
            $("#lcalle").show();
            $("#calle").empty();
            $("#main").text("Ingrese el piso y calle para iniciar la busqueda");
            var piso = parseInt($("#piso").children("option:selected").val() == "1");
            if(piso <= 1)
            {
                for(var i = 1; i < 25; i++)
                    $("#calle").append("<option value=" + i + " name=" + i + ">" + i + "</option>");
            }
            else
                for(var i = 1; i < 26; i++)
                    $("#calle").append("<option value=" + i + " name=" + i + ">" + i + "</option>");
        }
        else if (sector == "RO")
        {
            $("#lpiso").hide();
            $("#lcalle").hide();
            $("#main").text("Presione buscar para iniciar la busqueda")
        }
    });
    

    $(document).on('click','#leftArrow', function(){
        contador--;
        if (contador < 0)
            contador = 0;
        update(data[contador][0], data[contador][1], data[contador][2]);

    });

    $(document).on('click','#rightArrow', function(){
        contador++;
        if (contador > data.length-1)
            contador = data.length-1;
        update(data[contador][0], data[contador][1], data[contador][2]);
    });

    // Socket connection

    socketio.on('contador', function(msg){
        console.log(msg);
        $("#msg").text(msg);
    });
    socketio.on('clear', function(msg){
        console.log("Limpiar...");
        clearTable();
        data = [];
    });

    socketio.on('data', function(msg){
        console.log("Me llego esta data: " + msg[0] + " - " + msg[1]);
        restockTable(msg[0], msg[1], msg[2])
       
        if (data.length == 0){
            update(msg[0], msg[1], msg[2]);
        }
        data.push([msg[0], msg[1], msg[2]]);
    });
});

