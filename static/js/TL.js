var all_pos = [];
var MZ = [];
var RK = [];
var MZ2 = [];
var SI = [];
var rainbow = new Rainbow();
function update_all(sec)
{
    var tipo = 0;
    if (sec == "MZ-0" || sec == "MZ-1")
        tipo = 0;
    else if (sec == "MZ-2" || sec == "MZ-3")
        tipo = 1;
    else if (sec.substring(0, 2) == "RK")
    {
        tipo = 2;
        rainbow.setNumberRange(0, 1);   
        rainbow.setSpectrum("#71FF09", "#FF3C00");
    }
    if (tipo < 2)
        for (var calle=1; calle <= 27; calle++)
        {
            if (tipo == 0)
            {
                // Limpiando todos los canvas de todos los Mezzanine (full 86 modulos)
                for (var modulo=1; modulo <= 86; modulo++)
                {
                    $("#full_" + calle + "_" + modulo).css("opacity", 0);
                    if (calle + 27 <= 52)
                        $("#full2_" + (calle + 27) + "_" + modulo).css("opacity", 0);
                }
            }
            else if (tipo == 1)
            {
                for (var modulo=1; modulo <= 62; modulo++)
                {
                    // Limpiando todos los canvas de todos los Mezzanine (part 62 modulos)
                    $("#part_" + calle + "_" + modulo).css("opacity", 0);
                    if (calle + 27 <= 52)
                        $("#part2_" + (calle + 27) + "_" + modulo).css("opacity", 0);

                }
            }
        }
    else
    {
        for (var calle=2; calle <= 17; calle++)
        {
            for (var modulo = 1; modulo <= 104; modulo++)
            {
                for (var pos=1 ; pos <= 2; pos++)
                {
                    $("#RK_" + calle + "_" + modulo + "_" + pos).css("opacity", 0);
                }

            }
        }
    }
    var old_modulo = 0;
    var old_calle = 0;
    var total = 0;
    var contador = 0;
    var type = $("#type_heatmap").children("option:selected").val() == "VOLUMEN";
    if (tipo < 2)
    {
        if ($("#MZ_select").children("option:selected").val() == "MZ1")
        {
            data = google.visualization.arrayToDataTable([
                ['Tipo', 'Cantidad'],
                ["Disponible", MZ[0][sec]],
                ["Ocupada", MZ[2][sec]]
            ]);
        }
        else
        {
            data = google.visualization.arrayToDataTable([
                ['Tipo', 'Cantidad'],
                ["Disponible", MZ2[0]["MZ2-" + sec[3]]],
                ["Ocupada", MZ2[2]["MZ2-" + sec[3]]]
            ]);
        }

    }
    else
        data = google.visualization.arrayToDataTable([
            ['Tipo', 'Cantidad'],
            ["Disponible", RK[0][sec]],
            ["Ocupada", RK[2][sec]]
        ]);
    google.charts.setOnLoadCallback(drawChart);

    for (key in all_pos)
    {
        // Si el elemento de la lista tiene el mismo sector que el sector seleccionado Y 
        // El mezzanine seleccionado 
        var MZ_seleccion = ($("#MZ_select").children("option:selected").val() == "MZ1") ? 1 : 2;
        // Obtengo la calle del elemento en el array
        var calle = parseInt(key.substring(5, 8));
        /* Si (el SECTOR es igual al SECTOR SELECCIONADO [MZ] y 
                el MZ seleccionado es MZ1 y calle menor igual a 27 o 
                el MZ seleccionado es MZ2 y calle mayor igual a 28) o
                El sector es de RK.... 
        */
        if ((key.substring(0, 4) == sec || key.substring(0,2) == "RS" && "MZ-" + key[3] == sec) &&  // Si es MZ y 
        ((MZ_seleccion == 1 && calle <= 27) || // está seleccionado MZ1 y la calle es menor o igual a 27
        (MZ_seleccion == 2 && calle >= 28)) || "RK-" + key.substring(13, 15) == sec) // o, está seleccionado MZ2 y la calle es mayor o igual a 28
        {
            var modulo = parseInt(key.substring(9, 12));
            var pos = 0;
            // Si el tipo es 2 (Significado de RK)
            if (tipo == 2)
            {
                pos = parseInt(key.substring(16, 18));
                type = false; // Hardcodeo de que solo responda ante MELI debido a que en RK no se toma volumetría
            }
            // si el ciclo recién inicia...
            if (old_modulo == 0)
            {
                old_modulo = modulo;
                old_calle = calle;
                old_pos = pos;
                // Si type es verdadero (MODO VOLUMEN)
                if (type)
                    total = all_pos[key][0];
                else
                    // Sino, si el MELI es mayor a 4, tomarlo como 4
                    total = all_pos[key][1] > 4 ? 4 : all_pos[key][1];
                contador = 1;
            }

            /* Si (el modulo viejo es igual al modulo actual y el tipo es distinto de RK) o 
                  (la posición vieja es igual a la posición nueva y el tipo es RK)
            */         
            else if ((old_modulo == modulo && tipo != 2) || (old_pos == pos && tipo == 2))
            {
                // Si está en MODO VOLUMEN 
                if (type)
                        total+=all_pos[key][0];
                else
                    total += all_pos[key][1] > 4 ? 4 : all_pos[key][1];

                contador++;
            }
            else
            {
                // Elección de canvas según MZ seleccionado 
                var canvas_mezzanine = (MZ_seleccion == 1) ? "_" : "2_";
                // Si el contador es distinto de 0 (se reinició) y el tipo es MZ 
                if (contador != 0 && tipo < 2)
                    color = rainbow.colourAt(total/contador);
                else
                    color = rainbow.colourAt(total)
                
                if (!tipo)
                    $("#full" + canvas_mezzanine + old_calle + "_" + old_modulo).css({"background" : "#" + color, "opacity" : "0.8"});
                else if (tipo == 1)
                    $("#part" + canvas_mezzanine + old_calle + "_" + old_modulo).css({"background" : "#" + color, "opacity" : "0.8"});
                else
                    $("#RK_" + old_calle + "_" + old_modulo + "_" + old_pos).css({"background" : "#" + color, "opacity" : "0.8"});
                old_modulo = modulo;
                old_calle = calle;
                old_pos = pos;
                if (type)
                    total = all_pos[key][0];
                else
                    total = all_pos[key][1];
                contador = 1;
            }

        }
    }
    var canvas_mezzanine = (MZ_seleccion == 1) ? "_" : "2_";
    if (contador != 0 && tipo < 2)
        color = rainbow.colourAt(total/contador);
    else
        color = rainbow.colourAt(total)
        if (!tipo)
        {
            $("#full" + canvas_mezzanine + old_calle + "_" + old_modulo).css({"background" : "#" + color, "opacity" : "0.8"});

        }
    else if (tipo)
        $("#part" + canvas_mezzanine + old_calle + "_" + old_modulo).css({"background" : "#" + color, "opacity" : "0.8"});

}
function init(){

    $("#MZ").hide();
    $("#RK").hide();
    $("#SI").hide();
    $("#piechart").hide();
    $("#inicio").show();

}

function MZ_func(){
    $("#MZ").show();
    $("#inicio").hide();
    $("#SI").hide();

    $("#MZ_FLOOR").hide();
    $("#RK").hide();
    $("#MZ_PART").hide();
    $("#piechart").show();


    // Lleva la scrollbar arriba de todo
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0; 
}

function RK_func(){
    $("#RK").show();
    $("#SI").hide();

    $("#inicio").hide();
    $("#MZ_FLOOR").hide();
    $("#MZ").hide();
    $("#MZ_PART").hide();
    update_all("RK-0" + $("#nivel").children("option:selected").val());
    // Lleva la scrollbar arriba de todo
    $("#piechart").show();
    
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0; 
}

function SI_func(){
    $("#SI").show();
    $("#MZ").hide();
    $("#inicio").hide();
    $("#MZ_FLOOR").hide();
    $("#RK").hide();
    $("#MZ_PART").hide();
    $("#piechart").hide();


    // Lleva la scrollbar arriba de todo
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0; 
}

function MZ_FULL()
{
    $("#MZ").hide();
    $("#MZFULL_FLOOR").show();


}
var data;
function drawChart() 
{

    var options = {
      title: 'Metrica por espacio de MELI)',
      fontSize: 20
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options);
  }

function sortAllPos()
{
    var sorted_keys = [];
    for (key in all_pos)
    {
        sorted_keys[sorted_keys.length] = key;
    }
    sorted_keys.sort();

    var tempDict = {};
    for(var i = 0; i < sorted_keys.length; i++) {
        tempDict[sorted_keys[i]] = all_pos[sorted_keys[i]];
    }

    all_pos = tempDict;

}

$(function(){
    const socketio = io();
    // Seteo el espectro de los colores de rojo a verde
    rainbow.setSpectrum("#FF6347", "#ADFF2F");
    // MZ = returnMZ();
    // RK = returnRK();
    var CtrlDown = false, ctrlKey = 17, cKey = 67, xKey = 88;
    $(document).keydown(function(e)
    {
        if (e.keyCode == ctrlKey)
            CtrlDown = true;
        else
        {
            var buffer_copy = $("#buffer_copy");
            buffer_copy.show();
            if (CtrlDown && e.keyCode == cKey)
                buffer_copy.attr('value', $("#calle-ocupado").text().substring(6));
            else if (CtrlDown && e.keyCode == xKey)
                buffer_copy.attr('value', $("#calle-num").text());
            else
                return;
            buffer_copy.select();
            document.execCommand("copy");
            buffer_copy.hide();
        }
    })
                .keyup(function(e)
    {
        if (e.keyCode == ctrlKey)
            CtrlDown = false;   
    });


    socketio.emit('TL-data', '');
    socketio.on('TL-data', function(msg){
        all_pos = msg[0];
        sortAllPos();
        MZ = msg[1];
        RK = msg[2];
        MZ2 = msg[3];
        var disp = 0;
        var ocup = 0;
        var porcentaje = 0.0;
        function get_color(p3)
        {
            if (p3 > 80)
                return "#ADFF2F";
            else if (p3 <= 80  && p3 > 60)
                return "#FFFF00";
            else if (p3 <= 60 && p3 > 30)
                return "#FFD700";

            else if (p3 <= 30 && p3 > 0)
                return "#FF6347";
            return "#0000";
        }
        for (i=0; i<4; i++)
        {
            disp = MZ[0]["MZ-" + i];
            ocup = MZ[2]["MZ-" + i];
            porcentaje = disp * 100 / (disp + ocup);

            $("#MZ-" + i + " td").eq(1).text(disp);
            $("#MZ-" + i + " td").eq(2).text(ocup);            
            $("#MZ-" + i + " td").eq(3).text(porcentaje.toFixed(2)).css('background-color', get_color(porcentaje));

            disp = MZ2[0]["MZ2-" + i];
            ocup = MZ2[2]["MZ2-" + i];
            porcentaje = disp * 100 / (disp + ocup);

            $("#MZ2-" + i + " td").eq(1).text(disp);
            $("#MZ2-" + i + " td").eq(2).text(ocup);            
            $("#MZ2-" + i + " td").eq(3).text(porcentaje.toFixed(2)).css('background-color', get_color(porcentaje));
            j = i+2
            disp = RK[0]["RK-0" + (i+2)];
            ocup = RK[2]["RK-0" + (i+2)];
            porcentaje = disp * 100 / (disp + ocup);
            if (isNaN(porcentaje))
                porcentaje = 0
            $("#RK-" + j + " td").eq(1).text(disp);
            $("#RK-" + j + " td").eq(2).text(ocup);            
            $("#RK-" + j + " td").eq(3).text(porcentaje.toFixed(2)).css('background-color', get_color(porcentaje));
        }
        disp = RK[0]["RK-06"];
        ocup = RK[2]["RK-06"];
        porcentaje = disp * 100 / (disp + ocup);
        if (isNaN(porcentaje))
            porcentaje = 0
        $("#RK-6 td").eq(1).text(disp);
        $("#RK-6 td").eq(2).text(ocup);            
        $("#RK-6 td").eq(3).text(porcentaje.toFixed(2)).css('background-color', get_color(porcentaje));


    });
    $("#update_level").click(function()
    {
        if(confirm("Está a punto de actualizar la totalidad de RK, ¿está seguro que desea continuar?"))
            socketio.emit('update-RK', "");
    });

    $("#update_SI").click(function(){
        socketio.emit('pedir',["SI", -1, 0]);
    });

    $("#update_floor").click(function()
    {
        if(confirm("Está a punto de actualizar el piso en su totalidad, esta tarea podría relantizar la PC, ¿está seguro que desea continuar?"))
        {
            var sector = "";
            if ($("#MZ_select").children("option:selected").val() == "MZ2")
                sector = "MZ2-";
            else
                sector = "MZ-";

            socketio.emit('update-floor', sector + $("#floor_select").children("option:selected").val());
        }
    });

    $("#update_everything").click(function(){
        if(confirm("Está a punto de actualizar el CAD en su totalidad (MZ-RK-SI), esta tarea es muy pesada y no se puede parar, ¿está seguro que desea continuar?"))
            socketio.emit("update-everything", "");
    });
    socketio.on('TL-message', function(msg){
        $("#message").text(msg);
    });
    
    socketio.on("TL-update", function(msg){
        all_pos[msg[0]] = [msg[1], msg[2]];
        MZ = msg[3];
        RK = msg[4];
        MZ2 = msg[5];
        // Si el sector-piso concuerda con el sector + piso seleccionado... (MZ)
        if (msg[0].substring(0, 4) == "MZ-" + $("#floor_select").children("option:selected").val())
        {
            var contador = 0;
            var total = 1;
            var type = $("#type_heatmap").children("option:selected").val() == "VOLUMEN";
            var sec = $("#floor_select").children("option:selected").val();
            tipo = 0;
            // sec significa piso
            // si el piso es entre 0 y 1 entonces el tipo es 0
            if (sec == "0" || sec == "1")
            tipo = 0;
            // si el piso es entre 1 y 2 entonces el tipo es 1
            else if (sec == "2" || sec == "3")
            tipo = 1;
            else
                tipo = 2
            
            if (tipo < 2)
            {
                for (key in all_pos)
                {
                    // Si el modulo es igual al modulo de la dirección recibida...
                    if (key.substring(9, 12) == msg[0].substring(9, 12))
                    {
                        // Si el tipo de mapa es de VOLUMEN
                        if (type)
                            // Se suma el total en el 0 (volumen)
                            total += all_pos[key][0];
                        else // Sino
                            // Se suma el total en el 1 (cant. meli)
                            
                            total += all_pos[key][1]
                        contador++;
                    }
                }
                color = rainbow.colourAt(total/contador);
                var calle = parseInt(key.substring(5, 8));
                var modulo = parseInt(key.substring(9, 12));
                var dir = "";
                // Si el tipo es 0 (piso 0 o 1)
                if (!tipo)
                {
                    // Es el mapa completo (86)
                    if (calle < 27) // Si la calle es menor a 27, es del mezzanine 1
                        dir = "#full_";
                    else
                        dir = "#full2_";
                    $(dir + calle + "_" + modulo).css({"background" : "#" + color, "opacity" : "0.8"});

                }
                // Si el tipo es 1 (piso 1 o 2)
                // Es el mapa chico (62)
                else if (tipo)
                {   
                    if (calle < 27)
                        dir = "#part_";
                    else
                        dir = "#part2_"
                    $(dir + calle + "_" + modulo).css({"background" : "#" + color, "opacity" : "0.8"});
                }
            }

        }
        // Si la direccion recibida donde el sector- + nivel concuerda con RK-0 + nivel seleccionado....
        else if (msg[0].substring(0, 3) + msg[0].substring(13, 15) == "RK-0" + $("#nivel").children("option:selected").val())
        {
            var calle = parseInt(msg[0].substring(5, 8));
            var modulo = parseInt(msg[0].substring(9, 12));
            var posicion = parseInt(msg[0].substring(16, 18));
            rainbow.setNumberRange(0, 1);   
            rainbow.setSpectrum("#71FF09", "#FF3C00");

            $("#RK_" + calle + "_" + modulo + "_" + posicion).css({"background" : "#" + rainbow.colourAt(msg[2]), "opacity" : "0.8"});

        }
    });
    function leading_zero(num)
    {
        return (num<10?'0':'') + num
    }
    function date_to_string(date)
    {
        return leading_zero(date.getDate()) + "/" + leading_zero((date.getMonth()+1)) + "/" + date.getFullYear() + " " + leading_zero(date.getHours()) + ":" +leading_zero( date.getMinutes());
    }
    socketio.on('TL-SI', function(msg)
    {
        $("canvas[tipo='SI']").each(function(){
            $(this).css('background-color', "transparent");
        });
        var today = new Date();
        for (const direccion in msg)
        {
            for (const pallet in msg[direccion])
            {
                var fecha = msg[direccion][pallet][2];
                var dia = parseInt(fecha.substring(0, 2));
                var mes = parseInt(fecha.substring(3,5))-1;
                var ano = parseInt(fecha.substring(6, 10));
                var hora = parseInt(fecha.substring(11, 13));
                var minuto = parseInt(fecha.substring(14, 16));
                var date = new Date(ano, mes, dia, hora, minuto);
                msg[direccion][pallet][2] = date;
            }
        }  
        
        for (const key in msg)
        {
            msg[key].sort(function(a, b)
            {
            if (a[2] == "Invalid Date" || a[2] == '-' || b[2] == "Invalid Date" || b[2] == '-') 
            {
                return -1;
            }
            return a[2].getTime() > b[2].getTime(); 
            });
        }      
        var total_RK = 0;
        var total_MZ = 0;
        for (const key in msg)
        {
            var i = 0;
            for(const pallet in msg[key])
            {
                var date = msg[key][pallet][2];
                msg[key][pallet][2] = leading_zero(date.getDate()) + "/" + leading_zero(date.getMonth()) + "/" + date.getFullYear() + " " + leading_zero(date.getHours()) + ":" + leading_zero(date.getMinutes());
                var pallet_dir = msg[key][pallet][1];
                var ISs = msg[key][pallet][0];
                var calle = parseInt(key.substring(5,8));
                function makeIT(direccion)
                {
                    var hours = Math.abs(today - date) / 3.6e6;
                    var color = "";
                    if (hours > 48)
                        color = "#FF1B00";
                    else if (hours < 48 && hours > 24)
                        color = "#FF8B00";
                    else if (hours < 24 && hours > 12)
                        color = "#FFF300";
                    else
                        color = "#00FF16";
                    canvas = $("#" + direccion);
                    canvas.css('background-color', color);
                    canvas.attr("data-title", pallet_dir);
                    canvas.attr("data-content", ISs);
                    canvas.attr("horas", date_to_string(date));
                    canvas.attr("color", color);
                    try
                    {
                        var ctx = document.getElementById(direccion).getContext('2d');
                        ctx.font = "10px Arial";
                        ctx.clearRect(0, 0, canvas.attr('width'), canvas.attr('height'));
                        var number = date.getHours();

                        if (number < 10)
                            number = "0" + number;
                        ctx.fillText(number, 5, 15);                                     
                    }
                    catch{
                        console.log("ERROR con pos: " + direccion);

                    }
                    canvas.click(function(event)
                    {
                        $("#calle-num").text($(this).attr("data-title"));
                        $("#calle-ocupado").text("IS's: " + $(this).attr("data-content"));
                        $("#porcentaje-disponible").text("Fecha de llegada: " + $(this).attr("horas"));
                        var sz_div = parseInt($("#SI_BOX").css('width'));
                        var sz_box = parseInt($("#info-calle").css('width'));
                        $("#info-calle").css({"left" : (sz_div - event.pageX > sz_box-30 ? event.pageX : (event.pageX - sz_box*1.2)),
                                    "top" : event.pageY,
                                "display" : "block"});

                        $("#calle-disponible").hide();
                        
                    })
                        .mouseout(function(){
                            $("#info-calle").css("display","none");
                        });
                }
                switch(key.substring(0,2))
                {
                    case "SI":
                        {
                            var dir = "";
                            if ((i > 4 && (calle >= 11 && calle <= 50)) || i > 20 && (calle > 50))
                            {
                                $("#icon_extra_" + calle).show()
                                if (calle >= 11 && calle <= 50)
                                    total_MZ++;
                                else
                                    total_RK++;
                                continue;
                            }
                            else if (calle < 11)
                            {
                                dir = "SI_CPG_" + calle + "_" + (4-i);
                                total_MZ++;
                            }    
                            else if (calle >= 11 && calle <= 50)
                            {
                                dir = "SI_MZ_" + calle + "_" + (4-i);
                                total_MZ++;
                            }
                            else if (calle >= 51 && calle <= 54)
                            {
                                dir = "SI_MZ_" + calle + "_" + (20+(i-20));
                                total_MZ++;
                            }

                            else if (calle >= 90 && calle <= 94)
                            {
                                dir = "SI_RK_" + calle + "_" + (20+(i-20));
                                total_RK++;
                            }
                            makeIT(dir);
                            break;
                        }
                    case "WT":
                        {
                            var dir = "";
                            if (i > 1)
                            {
                                $("#icon_extra_WT_" + calle).show()
                                total_MZ++;
                                continue;
                            }
                            
                            total_MZ++;
                            makeIT("WT_" + calle);
                            break;
                        }
                    case "DK":
                        {
                            var dir = "";
                            if (i > 1)
                            {
                                $("#icon_extra_DK"+ calle).show();
                                if (calle < 57)
                                    total_MZ++;
                                else
                                    total_RK++;
                                continue;
                            }
                            if (calle < 57)
                                total_MZ++;
                            else
                                total_RK++;
                            makeIT("DK_" + calle);
                        }
                }
                i++;

            }
        }
        $("#total_pallets_MZ").text("Total pallets en MZ: " + total_MZ);
        $("#total_pallets_RK").text("Total pallets en RK: " + total_RK);

        SI = msg;

    });

    var last_open = "";
    $(".icon_clickeable").click(function()
    {
        var t = $(this);
        for(var j=0; j < 40; j++)
        {
            $("#SI_EXTRA_" + j).css('background-color', 'transparent')
                                .hide();
        }
        var pasar = true;
        
        for (key in SI)
        {
            if (key.substring(0,2) == $(this).attr('sector') && parseInt(key.substring(5,8)) == parseInt($(this).attr('calle')))
            {
                if (key == last_open)
                {
                    $("#extra_pallet").hide();
                    last_open = "";
                    pasar = false;
                    break;
                }
                last_open = key;
                var i = 5;
                SI[key].forEach(function(pallet, index)
                {
                    sector = key.substring(0, 2);
                    calle = parseInt(key.substring(5, 8));
                    if ((sector == "SI" && index < 5) 
                        || ((sector == "WT" || sector == "DK") && index < 1) 
                        || ((sector == "SI" && ((calle <= 54 && calle >= 51) || (calle >= 90 && calle <= 94))) && index < 20))
                        return;
                    var today = new Date();
                    var date = 0;
                    {
                        var fecha = pallet[2];
                        var dia = parseInt(fecha.substring(0, 2));
                        var mes = parseInt(fecha.substring(3,5));
                        var ano = parseInt(fecha.substring(6, 10));
                        var hora = parseInt(fecha.substring(11, 13));
                        var minuto = parseInt(fecha.substring(14, 16));
                        var date = new Date(ano, mes, dia, hora, minuto);
                    }
                    
                    var pallet_dir = pallet[1];
                    var ISs = pallet[0];
                    var dir = "SI_EXTRA_" +(i - 5);
                    var hours = Math.abs(today - date) / 3.6e6;
                    var color = "";
                    if (hours > 48)
                        color = "#FF1B00";
                    else if (hours < 48 && hours > 24)
                        color = "#FF8B00";
                    else if (hours < 24 && hours > 12)
                        color = "#FFF300";
                    else
                        color = "#00FF16";
                    canvas = $("#" + dir);
                    canvas.css('background-color', color);
                    canvas.css('top', parseInt(t.css('top')) + 60);
                    canvas.css('left', parseInt(t.css('left')) + 15);
                    canvas.css('display' , 'block');
                    canvas.attr("data-title", pallet_dir);
                    canvas.attr("data-content", ISs);
                    canvas.attr("horas", date_to_string(date));
                    canvas.attr("color", color);
                    try
                    {
                        var ctx = document.getElementById(dir).getContext('2d');
                        ctx.font = "10px Arial";
                        ctx.clearRect(0, 0, canvas.attr('width'), canvas.attr('height'));

                        var number = date.getHours();
                        if (number < 10)
                            number = "0" + number;
                        ctx.fillText(number, 5, 15);                                


                    }
                    catch{
                        console.log("ERROR con pos: " + dir);
                    }
                    canvas.click(function(event)
                    {
                        $("#calle-num").text($(this).attr("data-title"));
                        $("#calle-ocupado").text("IS's: " + $(this).attr("data-content"));
                        $("#porcentaje-disponible").text("Fecha de llegada: " + $(this).attr("horas"));
                        var sz_div = parseInt($("#SI_BOX").css('width'));
                        var sz_box = parseInt($("#info-calle").css('width'));
                        $("#info-calle").css({"left" : (sz_div - event.pageX > sz_box-30 ? event.pageX : (event.pageX - sz_box*1.2)),
                                            "top" : event.pageY,
                                        "display" : "block"})

                        $("#calle-disponible").hide();
                    })
                        .mouseout(function(){
                            $("#info-calle").css("display","none");
                        });
                    i++;

                });
            }
        }
        
        if (pasar)
            $("#extra_pallet").show()
                            .css({"top" : parseInt($(this).css('top')) + 30,
                                    "left" : parseInt($(this).css('left') + 40),
                                    "display" : "block"
                                })


        $("canvas[tipo='SI']").each(function(index){
            if($(this).attr('data-content') == undefined)
            {

            }
            
            else if ($(this).attr('data-content').includes($("#IS_search").val()) && $("#IS_search").val() != "" )
            {
                if (!$(this).hasClass("found"))
                {
                    $(this).addClass("found");
                    $(this).css('background-color', "#000000");
                }
            }
            else if ($(this).attr('data-title').includes($("#IS_search").val()) && $("#IS_search").val() != "")
            {
                if (!$(this).hasClass("found"))
                {
                    $(this).addClass("found");
                    $(this).css('background-color', "#000000");
                }
            }
            else
            {
                $(this).removeClass("found");
                $(this).css('background-color', $(this).attr('color'));
            }
        });
    });
    $("#MZ_SEL").click(function(){
        MZ_func();
    });

    $("#RK_SEL").click(function(){
        RK_func();
    });

    $("#SI_SEL").click(function()
    {
        SI_func();
    });
    $("#IS_search").change(function()
    {
        
        $("canvas[tipo='SI']").each(function(index){
            if($(this).attr('data-content') == undefined)
            {

            }
            
            // si tiene la IS...
            else if ($(this).attr('data-content').includes($("#IS_search").val()) && $("#IS_search").val() != "" )
            {
                if (!$(this).hasClass("found"))
                {
                    $(this).addClass("found");
                    $(this).css('background-color', "#000000");
                }
            }
            // si tiene el Pallet
            else if ($(this).attr('data-title').includes($("#IS_search").val()) && $("#IS_search").val() != "")
            {
                if (!$(this).hasClass("found"))
                {
                    $(this).addClass("found");
                    $(this).css('background-color', "#000000");
                }
            }
            else
            {
                $(this).removeClass("found");
                $(this).css('background-color', $(this).attr('color'));
            }
        });
        $(".icon_clickeable").each(function(index)
        {
            $(this).css('background-color', 'transparent');
        });
        for (arr in SI)
        {
            for (key in SI[arr])
            {
                if (SI[arr][key][0].includes($("#IS_search").val()) && $("#IS_search").val() != "" )
                {
                    var calle = parseInt(arr.substring(5,8));
                    $(".icon_clickeable[calle='"+ calle + "']").css('background-color', "#000000");
                }
                else if (SI[arr][key][1].includes($("#IS_search").val()) && $("#IS_search").val() != "" )
                {
                    var calle = parseInt(arr.substring(5,8));
                    $(".icon_clickeable[calle='"+ calle + "']").css('background-color', "#000000");
                }

            }
        }
    });
    $("#update").click(function(){
            socketio.emit('TL-data', '');
            update_all("MZ-" + $("#floor_select").children("option:selected").val());

        
    });
    $("#update_rk").click(function()
    {
        sortAllPos();
        update_all("RK-0" +  $("#nivel").children("option:selected").val());
    });
    $("#nivel").change(function(){
        update_all("RK-0" + $(this).children("option:selected").val());
    });
    $("#MZ_select").change(function(){
        // Si se selecciona MZ1
        if ($(this).children("option:selected").val() == "MZ1")
        {
            // Si la seleccion de piso es el piso 0 o 1 (FULL)
            if (parseInt($("#floor_select").children("option:selected").val()) < 2)
            {
                $("#MZ_FULL").css("display", "inline-block");
                $("#MZ_PART").css("display", "none");
                $("#MZ2_FULL").css("display", "none");
                $("#MZ2_PART").css("display", "none");

            }
            // Sino, si la seleccion de piso es de 2 o 3 (PART)
            else
            {
                $("#MZ_FULL").css("display", "none");
                $("#MZ_PART").css("display", "inline-block");
                $("#MZ2_FULL").css("display", "none");
                $("#MZ2_PART").css("display", "none");
            }
        }
        // Si se selecciona MZ2
        else
        {
            if (parseInt($("#floor_select").children("option:selected").val()) < 2)
            {
                $("#MZ2_FULL").css("display", "inline-block");
                $("#MZ2_PART").css("display", "none");
                $("#MZ_FULL").css("display", "none");
                $("#MZ_PART").css("display", "none");

            }
            // Sino, si la seleccion de piso es de 2 o 3 (PART)
            else
            {
                $("#MZ2_FULL").css("display", "none");
                $("#MZ2_PART").css("display", "inline-block");
                $("#MZ_FULL").css("display", "none");
                $("#MZ_PART").css("display", "none");
            }
        }
        

        update_all("MZ-" + $("#floor_select").children("option:selected").val());
    });
    $("#floor_select").change(function(){
        var seleccion = $(this).children("option:selected").val();
        // Si es entre el piso 0 o 1
        var MZNUM = ($("#MZ_select").children("option:selected").val() == "MZ1") ? 1 : 2; 
        if (this.value == 0 || this.value == 1)
        {
            // Si el piso es 0 y la el MZ1
            if (this.value == 0)
            {
                switch(MZNUM)
                {
                    case 1:
                    {
                        $("#MZ_FULL_0_IMG").show();
                        $("#MZ_FULL_IMG").hide();
                        $("#MZ_FULL").css("display", "inline-block");
                        $("#MZ_PART").css("display", "none");
                        $("#MZ2_FULL").css("display", "none");
                        $("#MZ2_PART").css("display", "none");
                        break;
                    }

                    case 2: 
                    {
                        $("#MZ2_FULL").css("display", "inline-block");
                        $("#MZ2_PART").css("display", "none");
                        $("#MZ_FULL").css("display", "none");
                        $("#MZ_PART").css("display", "none");
                        break;
                    }
                }
            }
            else
            {
                switch(MZNUM)
                {
                    case 1:
                    {
                        $("#MZ_FULL_IMG").show();
                        $("#MZ_FULL_0_IMG").hide();
                        $("#MZ_FULL").css("display", "inline-block");
                        $("#MZ_PART").css("display", "none");
                        $("#MZ2_FULL").css("display", "none");
                        $("#MZ2_PART").css("display", "none");
                        break;
                    }

                    case 2: 
                    {
                        $("#MZ2_FULL").css("display", "inline-block");
                        $("#MZ2_PART").css("display", "none");
                        $("#MZ_FULL").css("display", "none");
                        $("#MZ_PART").css("display", "none");
                        break;
                    }
                }
            }
            sortAllPos();
            update_all("MZ-" + seleccion);
        }
        else
        {
            switch(MZNUM)
            {
                case 1:
                {
                    $("#MZ_PART").css("display", "inline-block");
                    $("#MZ_FULL").css("display", "none");
                    $("#MZ2_FULL").css("display", "none");
                    $("#MZ2_PART").css("display", "none");
                    break;
                }

                case 2: 
                {
                    $("#MZ2_PART").css("display", "inline-block");
                    $("#MZ2_FULL").css("display", "none");
                    $("#MZ_FULL").css("display", "none");
                    $("#MZ_PART").css("display", "none");
                    break;
                }
            }
            sortAllPos();
            
            update_all("MZ-"+ seleccion);
        }
    });
    $("#type_heatmap").change(function(){
        if ($(this).children("option:selected").val() == "VOLUMEN")
        {
            rainbow.setNumberRange(0, 100);
            rainbow.setSpectrum("#FF3C00", "#71FF09");
        }
        else
        {
            rainbow.setNumberRange(0, 4);
            rainbow.setSpectrum("#71FF09", "#9EFF00", "#FFFE00", "#FFCA00", "#FF3C00");

        }
        sortAllPos();

        update_all("MZ-" + $("#floor_select").children("option:selected").val());
    });
    var salio = true;
    $("area").click(function(event){
        if (salio)
        {
            var num = $(this).attr("num");
            $("#calle-num").text("Calle " + num);
            if (num.length == 1)
                num = "00" + num;
            else if (num.length == 2)
                num = "0" + num;
            var pos_disponible = 0;
            var pos_ocupada = 0;
            var porcentaje = 0;
            for (var pos in all_pos)
            {
                if (pos.substring(0, 8) == "MZ-" + $("#floor_select").children("option:selected").val() + "-" + num
                ||
                    "RK-" + pos.substring(5, 8) + pos.substring(12, 15) == "RK-" + num + "-0" + $("#nivel").children("option:selected").val())
                {
                    if ((all_pos[pos][1] < 4 && pos.substring(0, 2) == "MZ") || 
                        all_pos[pos][1] == 0 && pos.substring(0, 2) == "RK")
                        pos_disponible++;
                    else
                        pos_ocupada++;
                }
            }
            porcentaje = pos_disponible * 100 / (pos_disponible + pos_ocupada);
            $("#calle-disponible").text("Disponible: " + pos_disponible);
            $("#calle-ocupado").text("Ocupado: " + pos_ocupada);
            $("#porcentaje-disponible").text("% disponibilidad: " + porcentaje.toFixed(2));
            $("#calle-disponible").css('display', "block");

            salio = false;
        }
        $("#info-calle").css({"left" : event.pageX ,
                             "top" : event.pageY,
                             "display" : "block"});
    })
             .mouseout(function(){
        $("#info-calle").css("display", "none");
        salio = true;
    });
    $(".clickeable").click(function(event)
    {  
        $("#calle-num_").text("Calle: " + $(this).attr("calle"));
        $("#calle-modulo").text("Modulo: " +  $(this).attr("modulo"));
        $("#calle-posicion").text("Posicion: " +  $(this).attr("posicion"));

        $("#info-modulo").css({"left": event.pageX,
                              "top": event.pageY,
                                "display": "block"});
        
    })
                    .mouseout(function(){
        $("#info-modulo").css("display", "none");
    });
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawChart);
    init();
})