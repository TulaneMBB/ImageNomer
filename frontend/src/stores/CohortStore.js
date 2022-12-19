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
            feats: [],
            subs: [],
            groups: [],
            display: null,
            corr: null,
            saved: [],
            labels: {}
        };
    },
    getters: {
        groupSelected: (state) => {
            return (type, task) => {
                let num = 0;
                return state[type].filter(item => {
                    const groups = state['groups'];
                    for (let i=0; i<groups.length; i++) {
                        if (groups[i].selected && groups[i].subs.indexOf(item.sub) != -1) {
                            if (!task || task == 'All' || getFnameField(item.fname, "task") == task) {
                                item.num = num++;
                                return true;
                            }
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
            return (field) => {
                const tasks = new Set();
                state[field].forEach(item => tasks.add(getFnameField(item.fname, 'task')));
                return [...tasks];
            };
        }
    },
    // actions
});