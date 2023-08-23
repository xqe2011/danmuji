<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title>{{ props.name }}</v-card-title>
        <v-chart ref="chart" class="chart" :option="option" autoresize/>
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
    },
    locked: {
        type: Boolean,
        required: true
    }
});

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent]);

const chart = ref(undefined) as Ref<InstanceType<typeof VChart> | undefined>;

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
        top: '3%',
        left: '1%',
        right: '0%',
        bottom: '0%',
        containLabel: true
    },
    dataZoom: [{
        type: 'inside',
        show: true,
        xAxisIndex: [0]
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
            type: 'value',
            
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
    const series: {data: number[]}[] = [];
    props.data.forEach((item, index) => {
        series[index] = {
            data: item as any as number[]
        }
    });
    chart?.value?.setOption({
        series: series
    });
    if (props.locked) {
        chart.value?.setOption({
            dataZoom: [{
                startValue: (props.data[0] as number[]).length - 10,
                endValue: (props.data[0] as number[]).length - 1
            }]
        });
    }
});
</script>
