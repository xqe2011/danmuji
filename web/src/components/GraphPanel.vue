<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title tabindex="2">{{ props.name }}</v-card-title>
        <v-chart class="chart" :option="option" />
    </v-card>
</template>

<style scoped>
.v-card {
    display: flex;
    flex-direction: column;
}

.chart {
    height: 400px;
}
</style>
  
<script setup lang="ts">
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart } from "echarts/charts";
import { TitleComponent, TooltipComponent, LegendComponent, DataZoomComponent, GridComponent } from "echarts/components";
import VChart from "vue-echarts";
import { ref, watch } from "vue";
import { Ref } from "vue";

const props = defineProps({
    name: {
        type: String,
        required: true
    },
    data: {
        type: Array,
        required: true
    },
    columes: {
        type: Array,
        required: true
    }
});

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent]);

const option = ref({
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            label: {
                backgroundColor: '#6a7985'
            }
        }
    },
    legend: {},
    grid: {
        top: '0%',
        left: '0%',
        right: '0%',
        bottom: '0%'
    },
    dataZoom: [{
        type: 'inside',
        show: true,
        xAxisIndex: [0],
        startValue: 0,
        end: 100
    }],
    xAxis: [
        {
            type: 'category',
            boundaryGap: false,
            show: false
        }
    ],
    yAxis: [
        {
            type: 'value'
        }
    ],
    series: [] as any[]
});

props.columes.forEach((item, index) => {
    option.value.series.push({
        name: item,
        type: 'line',
        stack: 'Total',
        areaStyle: {},
        data: []
    });
    if (props.data.length != 0)
        option.value.series[index].data = props.data[index];
});
watch(props, () => {
    props.data.forEach((item, index) => {
        option.value.series[index].data = item;
    });
    option.value.dataZoom[0].startValue = (props.data[0] as number[]).length - 10;
});
</script>
