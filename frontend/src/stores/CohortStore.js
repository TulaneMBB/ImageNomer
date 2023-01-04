import { defineStore } from 'pinia';
import { getFnameField } from './../functions.js';

export const useCohortStore = defineStore("CohortStore", {
    state: () => {
        return {
            fctype: 'fc',
            fc: [], 
            partial: [],
            demo: {},
            weights: [],
            subs: [],
            groups: [],
            display: null,
            corr: null,
            p: null,
            saved: [],
            labels: {}
        };
    },
    getters: {
        // selected and groupSelected:
        // NOTE: maybe required to say state['groups'] not state.groups
        groupSelected: (state) => {
            return (type, task) => {
                return state[type].filter(item => {
                    const groups = state['groups'];
                    for (let i=0; i<groups.length; i++) {
                        if (!groups[i].selected)
                            continue;
                        if (groups[i].subs.indexOf(item.sub) == -1) 
                            continue
                        return !task || task == 'All' || 
                            getFnameField(item.fname, 'task') == task;
                    }
                    return false;
                });
            };
        },
        selected(state) {
            return (type, task) => {
                const subs = state['subs']
                    .filter(elt => elt.selected)
                    .map(elt => elt.id); 
                if (!type) {
                    return subs;
                }
                return state[type]
                    .filter(elt => {
                        return !task || task == 'All' 
                            || getFnameField(elt.fname, 'task') == task;
                    })
                    .filter(elt => subs.indexOf(elt.sub) != -1);
            };
        },
        summary: (state) => {
            return (field) => {
                const vals = Object.values(state.demo[field]);
                if (!isNaN(vals[0])) {
                    const min = Math.min(...vals).toFixed(1);
                    const max = Math.max(...vals).toFixed(1);
                    const mean = (vals.reduce((prev, cur) => prev+cur, 0)
                        /vals.length).toFixed(1);
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
                if (!state[field]) return [];
                state[field].forEach(
                    item => tasks.add(getFnameField(item.fname, 'task')));
                return [...tasks];
            };
        }
    },
    // actions
});
