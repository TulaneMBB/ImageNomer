import { defineStore } from 'pinia';
import { enc, getFnameField } from './../functions.js';

export const useCohortStore = defineStore("CohortStore", {
    state: () => {
        return {
            cohort: null,
            cohorts: [],
            fctype: 'fc',
            snps: {},
            fc: [], 
            partial: [],
            demo: {},
            weights: [],
            decomp: [],
            subs: [],
            groups: [],
            display: null,
            corr: null,
            p: null,
            saved: [],
            labels: {},
            mathImage: null,
        };
    },
    getters: {
        // selected and groupSelected:
        // NOTE: maybe required to say state['groups'] not state.groups
        groupSelected: (state) => {
            return (type, task) => {
                const fcArr = type == 'snps' 
                    ? state[type][task]
                    : state[type];
                return fcArr.filter(item => {
                    const groups = state['groups'];
                    for (let i=0; i<groups.length; i++) {
                        if (!groups[i].selected)
                            continue;
                        if (groups[i].subs.indexOf(item.sub) == -1) 
                            continue
                        if (type == 'snps')
                            return true;
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
                if (type == 'snps') {
                    return state[type][task]
                    .filter(elt => subs.indexOf(elt.sub) != -1);
                }
                return state[type]
                    .filter(elt => {
                        return !task || task == 'All' 
                            || getFnameField(elt.fname, 'task') == task;
                    })
                    .filter(elt => subs.indexOf(elt.sub) != -1);
            };
        },
        snpsSets: (state) => {
            return Object.keys(state['snps']);
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
                } else {
                    // Should contain the above as a special case
                    // Count number of distinct values
                    const valset = new Set();
                    const valcounts = {};
                    const valcounts2 = [];
                    vals.forEach(v => valset.add(v));
                    valset.forEach(v => {
                        valcounts[v] = 0;
                    });
                    vals.forEach(v => {
                        valcounts[v]++;
                    });
                    for (let v in valcounts) {
                        valcounts2.push([v, valcounts[v]]);
                    }
                    valcounts2.sort((a,b) => b[1] - a[1]);
                    let sum = valcounts2.slice(0,5).map(vc => `${vc[0]}: ${vc[1]}`).join(' ');
                    if (valcounts2.length > 5) {
                        sum += `... (${valcounts2.length-5} others)`;
                    }
                    sum += ` (n = ${vals.length})`
                    return sum;
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
    actions: {
        fetchCohort(cohort) {
            fetch(`/data/info?cohort=${enc(cohort)}`)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json.err);
                    return;
                }
                this.fc = json.fc ? this.parseFC(json.fc) : [];
                this.partial = json.partial ? this.parseFC(json.partial) : [];
                this.snps = json.snps ? this.parseSNPs(json.snps) : {};
                this.demo = json.demo;
                this.subs = this.getSubs(json.demo);
                this.weights = json.weights;
                this.groups = [{query: 'All', 
                    subs: this.subs.map(sub => sub.id)}];
                this.decomp = json.decomp;
            })
            .catch(err => console.log(err));
        },
        getCohorts() {
            fetch(`/data/cohorts`)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json.err);
                    return;
                }
                this.cohorts = json.cohorts;
                this.cohort = this.cohorts[0];
                this.fetchCohort(this.cohort);
            })
            .catch(err => console.log(err));
        },
        getSubs(demo) {
            let subs = new Set();
            for (let key in demo) {
                Object.keys(demo[key]).forEach(
                    sub => subs.add(sub));
            }
            subs = [...subs].map(sub => ({id: sub, selected: false}));
            return subs;
        },
        parseFC(jsonfc) {
            // id is just an index (from the map call)
            jsonfc.sort();
            return jsonfc.map((fname, idx) => {
                return {
                    id: idx, 
                    fname: fname, 
                    ...this.parseFname(fname) 
                }
            });
        },
        parseFname(fname) {
            const sub = fname.split('_')[0];
            const task = getFnameField(fname, 'task');
            return {
                sub, task
            }
        },
        parseSNPs(jsonsnps) {
            // id is just an index
            // set comes from json object key, unlike with task in FCs
            for (let set in jsonsnps) {
                jsonsnps[set] = jsonsnps[set]
                .map((fname, idx) => {
                    const sub = fname.split('_')[0];
                    return {
                        id: idx,
                        fname,
                        sub
                    }
                });
            }
            return jsonsnps;
        }
    }
});
