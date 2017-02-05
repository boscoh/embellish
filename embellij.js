#!/usr/bin/env node

/**
 * Rewrite of my embellish.py package.
 * Improvements:
 *  - commonark instead of vanilla markdown
 *  - pug instead of pyhaml
 *  - yaml frontmatter consistent with jeckyl
 *  - better JSON integration
 */

"use strict";

const fs = require('fs-extra');
const path = require('path');
const _ = require('lodash');
const nopt = require('nopt');
const slug = require('slug');
const globule = require('globule');
const pug = require("pug");
const normalize = require('normalization');
const yaml = require('yamljs');
const dateFormat = require('dateformat');
const commonmark = require('commonmark');
const crypto = require('crypto');
const yamlFront = require('yaml-front-matter');

function isFile(f) {
  try {
    return fs.lstatSync(f).isFile();
  }
  catch (e) {
    return false;
  }
}

function isDirectory(file) {
  try {
    return fs.lstatSync(file).isDirectory();
  }
  catch (e) {
    return false;
  }
}

function hash(text) {
  return crypto.createHash('md5').update(text).digest("hex");
}

function pprint(name, obj) {
  console.log(name, '=', JSON.stringify(obj, null, 2));
}

function stripExtOfPathname(filename) {
  let n = filename.length - path.extname(filename).length;
  return filename.substring(0, n);
}

function splitByThreeDashes(text, nMaxPiece) {
	let lines = text.split(/\r?\n/);
	let pieces = [];
	pieces.push("");
	let iPiece = 0;
	for (let line of lines) {
		if (line.match(/^---/) && (iPiece < nMaxPiece-1)) {
			pieces.push("");
			iPiece += 1;
		} else {
			pieces[iPiece] += line + "\n";
		}
	}
	return pieces;
}

function convertUnicodeCharsToHtml(str) {
    let strLength = str.length;
    if (strLength === 0) {
        return '';
    }
    let result = '';
    let i = 0;
    while (i < strLength) {
        let c = str.charCodeAt(i);
        if (c <= 127) {
            result += str[i++];
            continue;
        }
        result += '&#' + c + ';';
        i++
    }
    return result;
}

function getFiles(dir, exts, recursive) {
  let files = [];
  let fileTag;
  for (let ext of exts) {
    if (recursive) {
      fileTag = path.join(dir, `**/*${ext}`);
    } else {
      fileTag = path.join(dir, `*${ext}`);
    }
    files = _.concat(files, globule.find(fileTag));
  }
  return files;
}

function convertCommonmarkToHtml(text) {
	let reader = new commonmark.Parser();
	let writer = new commonmark.HtmlRenderer();
	let parsed = reader.parse(text);
	return convertUnicodeCharsToHtml(writer.render(parsed));
}

function getModifiedDate(file) {
  let stats = fs.statSync(file);
  return new Date(stats.mtime);
}

let defaultPage = {
  template: 'default.pug',  // name of template file
  filename: null,  // name of markdown file
  checksum: '', // checksum used to check final output to avoid redundant writes
  excerpt: '', // text to put in excerpt, no tags please!
  content: '',  // main text of article
  title: '',  // title for indexing and for large display
  category: '',  // category of article for indexing
  relSiteUrl: '',  // the top site directory relative to this page
  date: null,  // published date
  slug: null,  // url-safe name of article used to make url and files
  url: '',   // relative url used for links in index files
  target: '',    // target filename, maybe different to url due to redirection
  index: false,   // indicates if this is an indexing page
  sortKey: null,  // the field on which to sort under in indexing
  sortReverse: true,  // ascending or descing order for sorting
  subpages: [],   // in indexing, pages belonging to the index placed here
  maxSubpages: null,  // a maximum limit of files to put in subpages
};


function readPages(site) {
  let readExts = site.readExts;
  let recursive = site.recursive;

  if (site.contentDir) {
    let files = getFiles(site.contentDir, readExts, recursive);
    site.files = _.concat(site.files, files);
  }

  let cachedPages = {};
  for (let page of site.pages) {
    cachedPages[page.filename] = page;
  }
  site.pages = [];

  console.log(`readSiteFiles ${site.files.length}`);
  for (let file of site.files) {

    let page = _.cloneDeep(defaultPage);
    if (_.has(cachedPages, file)) {
      _.assign(page, cachedPages[file]);
    }
    page.filename = file;

    _.assign(page, yamlFront.loadFront(file, 'content'))
    page.content = convertCommonmarkToHtml(page.content)

    if (page.date) {
      page.date = new Date(page.date);
    }
    if (!page.slug) {
      let name = path.basename(stripExtOfPathname(page.filename));
      page.slug = slug(normalize(name));
    }
    page.content = convertCommonmarkToHtml(page.content);
    if (!page.url) {
      let dirname = path.dirname(page.filename);
      let full_url = path.join(dirname, page.slug + site.writeExt);
      page.url = path.relative(site.contentDir, full_url);
    }
    if (!page.target) {
      page.target = page.url;
    }
    page.relSiteUrl = path.relative(path.dirname(page.target), ".");
    if (!page.relSiteUrl) {
      page.relSiteUrl = ".";
    }

    site.pages.push(page);
  }
}

function generateIndexableSubpages(site) {
  for (let page of site.pages) {
    if (page.index) {
      let subpages = _.omitBy(site.pages, { index: true });
      if (page.category) {
        subpages = _.filter(subpages, {category: page.category})
      }
      if (page.sortKey) {
        subpages = _.sortBy(subpages, page.sortKey);
        if (page.sortReverse) {
          subpages = _.reverse(subpages);
        }
      }
      if (page.maxSubpages) {
        subpages = _.take(subpages, page.maxSubpages);
      }
      page.subpages = subpages;
      let n = page.subpages.length;
      console.log(`generateIndexableSubpages ${page.url} ${n}`);
    }
  }
}

function getTemplateDir(page, site) {
  let templateDirs = [
    path.dirname(page.filename),
    site.templateDir,
    path.join(__dirname, 'defaults')
  ];

  for (let templateDir of templateDirs) {
    let template = path.join(templateDir, page.template);
    if (fs.existsSync(template)) {
      return template;
    }
  }
  return null
}

function formatPageDates(page, dateFormatString) {
  page.date = dateFormat(page.date, dateFormatString);

}

function writePages(site) {

  // must change all pages first due to referencing through subpages
  let nSkip = 0;
  for (let page of site.pages) {

    let dateFormatString = site.dateFormatString;
    if (page.dateFormatString) {
      dateFormatString = page.dateFormatString;
    }
    for (let subpage of page.subpages) {
      formatPageDates(subpage, dateFormatString);
    }
    formatPageDates(page, dateFormatString);

    let outHtml = path.join(site.outputDir, page.target);

    let template = getTemplateDir(page, site);

    let modified = getModifiedDate(page.filename);

    let isChecksumSame = true;
    let checksum = hash(page.content);
    if (checksum != page.checksum) {
      isChecksumSame = false;
      page.checksum = checksum;
    }

    if (isChecksumSame) {
      nSkip += 1;
      continue;
    }
    
    if (!_.endsWith(template, 'pug')) {
      continue;
    }
    let compileWithMetadata = pug.compileFile(template, { pretty: true });
    let text = compileWithMetadata({page, site});

    fs.ensureDir(path.dirname(outHtml));
    console.log(`writeSiteFiles (${template}) => ${outHtml}`);
    fs.writeFileSync(outHtml, text);
  }

  if (nSkip) {
    console.log(`writeSiteFiles no changes ${nSkip} files`)
  }
}

function processSite(site) {
  if (!site.forced &&isFile(site.cachedPages)) {
    console.log(`processSite cachedPages ${site.cachedPages}`);
    let text = fs.readFileSync(site.cachedPages, 'utf8');
    site.pages = _.concat(site.pages, JSON.parse(text));
  }

  readPages(site);
  generateIndexableSubpages(site);
  writePages(site);
  fs.copy(site.mediaDir, site.outputDir);

  if (site.cachedPages) {
    console.log(`processSite saveCachedPages ${site.cachedPages}`);
    _.map(site.pages, (page) => { page.subpages = []; });
    fs.writeFileSync(site.cachedPages, JSON.stringify(site.pages));
  }
}


{
  const doc = `
  embelij - a static site generator

  usage: embelij [-s SITE.yaml] [-r] (markdown | directory)
  `;

  let knownOpts = {
    "site": [String, null],
    "recursive": Boolean
  };

  let shortHands = {
    "r": ["--recursive"],
    "s": ["--site"]
  };

  let parsed = nopt(knownOpts, shortHands, process.argv, 2);

  if (!parsed.site && parsed.argv.remain.length == 0) {
    console.log(doc);
    return
  }

  let site = {
    url: '', // if '' then use relative urls
    outputDir: '.',  // generated files and static files put here
    files: [], // list of all files to be converted
    contentDir: '.',  // look for markdown files
    pages: [],  // stores all the processed pages found in 'content_dir'
    templateDir: '.',  // look for templates
    mediaDir: '.',  // files to be copied directly into the output directory
    cachedPages: 'site.cache',  // if not empty, caching file to spend updates
    readExts: ['.md', '.txt'],
    writeExt: '.html', // extensions to converted html
    dateFormatString: "fullDate", // the formatting of page.date 
    recursive: false, // search all subdirectories in contentDir
    force: false, // don't use cache, process all files
  };

  site.recursive = parsed.recursive;
  site.force = parsed.force;

  if (parsed.site) {
    console.log(`loadSiteConfig ${parsed.site}`);
    let text = fs.readFileSync(parsed.site, 'utf8')
    _.assign(site, yaml.parse(text))
  }

  for (let file of parsed.argv.remain) {
    if (isFile(file)) {
      console.log(`readSiteFiles (file) => ${file}`);
      site.files.push(file);
    }
    if (isDirectory(file)) {
      console.log(`readSiteFiles (directory) => ${file}`);
      let files = getFiles(file, site.readExts, site.recursive)
      site.files = _.concat(site.files, files);
    }
  }

  processSite(site);

}




