import * as home from './home.js';
import * as builds from './builds.js';
import * as build from './build.js';
import * as workshop from './workshop.js';
import * as arsenal from './arsenal.js';
import * as item from './item.js';
import * as mutations from './mutations.js';
import * as tiers from './tiers.js';
import * as routes from './routes.js';
import * as world from './world.js';
import * as biome from './biome.js';
import * as boss from './boss.js';
import * as bc from './bc.js';
import * as unlocks from './unlocks.js';
import * as outfits from './outfits.js';
import * as knowledge from './knowledge.js';
import * as about from './about.js';
import * as notFound from './notfound.js';

const table = {
  '': home, builds, build, workshop, arsenal, item, mutations, mutation: item, tiers, routes, world, biome, boss, bc, unlocks, outfits, knowledge, about,
};

export const resolve = (path) => table[path] ?? notFound;
