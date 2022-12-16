import { defineStore } from 'pinia';

function getFnameField(fname, field) {
    let val = null;
    fname.split('_').forEach(part => {
        const pp = part.split('-');
        if (pp.length == 2 && pp[0] == field) {
            val = pp[1];
        }
    });
    return val;
}

export const useCohortStore = defineStore("CohortStore", {
    state: () => {
        return {
            fc: [], 
            demo: {},
            subs: [],
            groups: [],
            display: null,
            corr: null,
        };
    },
    getters: {
        groupSelected: (state) => {
            return (type) => {
                let num = 0;
                return state[type].filter(item => {
                    const groups = state['groups'];
                    for (let i=0; i<groups.length; i++) {
                        if (groups[i].selected && groups[i].subs.indexOf(item.sub) != -1) {
                            item.num = num++;
                            return true;
                        }
                    }
                    return false;
                });
            };
        },
        selected: (state) => {
            return (type) => state[type].filter(elt => elt.selected);
        },
        summary: (state) => {
            return (field) => {
                const vals = Object.values(state.demo[field]);
                if (!isNaN(vals[0])) {
                    const min = Math.min(...vals).toFixed(1);
                    const max = Math.max(...vals).toFixed(1);
                    const mean = (vals.reduce((prev, cur) => prev+cur, 0)/vals.length).toFixed(1);
                    return `min: ${min} mean: ${mean} max: ${max} (n=${vals.length})`;
                } else if (vals[0] == 'M' || vals[0] == 'F') {
                    let m = 0;
                    let f = 0;
                    vals.forEach(val => {
                        if (val == 'M') m++;
                        else if (val == 'F') f++;
                    });
                    return `male: ${m} female: ${f} (n=${vals.length})`
                }
            }
        },
        tasks: (state) => {
            const tasks = new Set();
            state.fc.forEach(fc => tasks.add(getFnameField(fc.fname, 'task')));
            return [...tasks];
        }
    },
    // actions
});