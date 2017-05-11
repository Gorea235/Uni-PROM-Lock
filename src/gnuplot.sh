#! /usr/bin/gnuplot -persist
set title 'Access Times';
set ylabel 'Pass/Fail';
set xlabel 'Time Since Midnight';
set grid;
set term jpeg;
set output 'access_times_graph.jpg';
set yrange [-1:2];
plot "gnuplot_data.csv" using 1:2 pt 7 ps 2;
