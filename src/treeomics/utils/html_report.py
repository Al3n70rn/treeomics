#!/usr/bin/python
"""Helper functions to generate report in HTML"""
__author__ = 'Johannes REITER'
__date__ = 'March 6, 2015'

import logging
import os
import numpy as np
import datetime
import math
from utils.int_settings import VERSION
import settings


# get logger for application
logger = logging.getLogger('treeomics')


class HTMLReport(object):
    """
    Generates an HTML formatted file providing an overview about the data and the results
    """

    def __init__(self, file_path, patient_name):
        """
        Opens the output file
        :param file_path: path to the output file of the created HTML report
        :param patient_name: name of the subject
        """

        self.file = open(file_path, 'w')
        self.patient_name = patient_name

        self._ind = 0      # current indentation
        self._inds = ['\t'*i for i in range(10)]    # indentation

    def start_report(self):
        """
        Add HTML header and other basics to the report
        """

        # write HTML page header
        self.file.write('<!DOCTYPE html>\n')
        self.file.write('<html lang="en">\n')
        self._ind += 1      # indentation level increases by 1

        self.file.write(self._inds[self._ind]+'<head>\n')
        self._ind += 1      # indentation level increases by 1

        self.file.write(self._inds[self._ind]+'<meta charset="utf-8">\n')
        self.file.write(self._inds[self._ind]+'<meta http-equiv="X-UA-Compatible" content="IE=edge">\n')
        self.file.write(self._inds[self._ind]+'<meta name="viewport" content="width=device-width, initial-scale=1">\n')
        self.file.write(self._inds[self._ind]
                        + '<meta name="description" content="Treeomics analysis report of patient {}">\n'
                        .format(self.patient_name))
        self.file.write(self._inds[self._ind]+'<meta name="author" content="Johannes G. Reiter">\n\n')
        self.file.write(self._inds[self._ind]+'<title>Treeomics analysis report of patient {}</title>\n'
                        .format(self.patient_name))
        self.file.write(self._inds[self._ind]+'<link rel="stylesheet" '
                        'href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css">\n')
        self.file.write(self._inds[self._ind]+'<style>body{ margin:0 100; background:white; }</style>\n')
        # self.file.write(self._inds[self._ind]+'<style>body{ margin:0 100; background:whitesmoke; }</style>\n')

        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</head>\n\n')

        self.file.write(self._inds[self._ind]+'<body>\n')
        self._ind += 1      # indentation level increases by 1
        self.file.write(self._inds[self._ind]+'<div class="container" style="max-width:900px">\n')
        self._ind += 1      # indentation level increases by 1
        self.file.write(self._inds[self._ind]+'<div class="page-header">\n')
        self._ind += 1      # indentation level increases by 1
        self.file.write(self._inds[self._ind]+'<h2>Treeomics analysis report of patient {}</h2>\n'
                        .format(self.patient_name))
        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</div>\n')

    def add_sequencing_information(self, patient, mut_table_path=None):
        """
        Adds basic information about the provided sequencing data and if provided add a mutation table plot
        :param patient: instance of class patient
        :param mut_table_path: path to the generated mutation table plot
        """

        self.file.write(self._inds[self._ind]+'<h4>Input data</h4>\n')

        self.file.write(self._inds[self._ind]
                        + '<table class="table table-striped" '
                        + 'style="text-align: center;width:98%;max-width:800px;font-size:9pt">\n')
        self._ind += 1      # indentation level increases by 1
        col_names = ['Sample', 'Median coverage (mean)', 'Median MAF (mean)', 'Purity',
                     'No variants present', 'absent']
        header = ''.join('<th class="text-center">{}</th>'.format(col_name) for col_name in col_names)
        self.file.write(self._inds[self._ind]+header+'\n')

        pres_lp = math.log(0.5)  # log probability of 50%
        # build up output data sequentially
        for sa_idx, sample_name in enumerate(patient.sample_names):

            row = list()
            row.append(sample_name.replace('_', ' '))

            row.append('{:.1f} ({:.1f})'.format(np.median(patient.sample_coverages[sample_name]),
                                                np.mean(patient.sample_coverages[sample_name])))
            # if patient.sample_dis_phred_coverages is not None:
            #     row.append(np.median(patient.sample_dis_phred_coverages[sample_name]))
            # else:
            #     row.append('n/a')

            row.append('{:.1%} ({:.1%})'.format(np.median(patient.sample_mafs[sample_name]),
                                                np.mean(patient.sample_mafs[sample_name])))

            # estimated purity
            if sample_name in patient.estimated_purities:
                row.append('{:.1%}'.format(patient.estimated_purities[sample_name]))
            else:
                row.append('-')

            # Bayesian inference model classification
            # present if probability to be present is greater than 50%
            row.append(sum(1 for ps in patient.log_p01.values() if ps[sa_idx][1] > pres_lp))
            row.append(sum(1 for ps in patient.log_p01.values() if ps[sa_idx][1] <= pres_lp))

            # # Previous conventional classification
            # row.append(patient.positives[sample_name])
            # row.append(patient.negatives[sample_name])
            # row.append(patient.unknowns[0][sample_name]+patient.unknowns[1][sample_name])

            # write row to file
            self.file.write(self._inds[self._ind]+'<tr>'+''.join('<td>{}</td>'.format(c) for c in row)+'</tr>\n')

        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</table>\n')

        # provide general summary about the samples
        self.file.write(self._inds[self._ind]+'<p>\n')
        self._ind += 1      # indentation level increases by 1
        self.file.write(self._inds[self._ind]+'Samples that passed the filtering: {}/{}</br>\n'.format(
            len(patient.sample_names), len(patient.sample_names) + len(patient.discarded_samples)))
        # median and mean coverage
        coverages = []
        for mut_key in patient.mut_reads.keys():
            # for sample_name in patient.mut_reads[mut_key].keys():     # all samples
            for sample_name in patient.sample_names:
                if patient.coverage[mut_key][sample_name] >= 0:
                    coverages.append(patient.coverage[mut_key][sample_name])
        self.file.write(self._inds[self._ind]+'Median coverage in the passed samples: {} (mean: {:.2f})'
                        .format(np.median(coverages), np.mean(coverages))+'\n')
        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</p>\n')

        # provide general summary about the variants
        self.file.write(self._inds[self._ind]+'<p>\n')
        self._ind += 1      # indentation level increases by 1
        self.file.write(self._inds[self._ind]+'Total number of passed somatic variants: {} </br>\n'.format(
            len(patient.mutations)))
        self.file.write(self._inds[self._ind]+'Variants classified as present in at least one of the samples '
                                              'that passed the filtering: {} </br>\n'.format(
                                              len(patient.present_mutations)))

        # self.file.write(self._inds[self._ind]+'Mean number of variants per sample: {:.1f} </br>\n'.format(
        #                 (float(sum(len(muts) for sa_idx, muts in patient.samples.items()))
        #                  / len(patient.sample_names))))

        self.file.write(self._inds[self._ind]+"Founders (variants present in all samples): {} ({:.1%}) </br>\n".format(
            len(patient.founders), float(len(patient.founders))/len(patient.present_mutations) if
            len(patient.present_mutations) > 0 else float('nan')))
        self.file.write(self._inds[self._ind] +
                        'Mean number of unique (private) variants per sample: {:.1f} ({:.1%}) </br>\n'
                        .format(float(len(patient.shared_muts[1])) / len(patient.sample_names),
                                (float(len(patient.shared_muts[1])) / len(patient.sample_names)) /
                        (sum(len(muts) for sa_idx, muts in patient.samples.items()) / len(patient.sample_names))))

        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</p>\n')

        if mut_table_path is not None:

            self.file.write(self._inds[self._ind]+'<div align="center">\n')
            self.file.write(self._inds[self._ind]+'<div style="width:98%;max-width:800px">\n')
            self._ind += 1      # indentation level increases by 1

            self.file.write(self._inds[self._ind]+'<figure>\n')
            self._ind += 1      # indentation level increases by 1
            self.file.write(self._inds[self._ind]+'<img class="img-responsive" src="'+mut_table_path +
                                                  '" alt="Variant classification table" width="800"/>'+'\n')
            self.file.write(self._inds[self._ind]+'<div align="left">\n')
            self.file.write(self._inds[self._ind]+'<figcaption>\n')
            self.file.write(
                self._inds[self._ind]+'<b>Probabilistic variant classification across '
                + '{} samples of patient {}.</b>\n'.format(len(patient.sample_names), patient.name))
            self.file.write(self._inds[self._ind]+'Blue rectangles correspond to present variants, '
                            + 'red to absent variants, and white to unknown mutation status. '
                              'Brighter colors denote higher probability. \n')
            # self.file.write(
            #     self._inds[self._ind]+'In total {} distinct variants were classified as present in at least one sample'
            #         .format(len(patient.present_mutations)) + ', {} ({:.1%}) of those were founders, \n'.format(
            #         len(patient.founders), float(len(patient.founders))/len(patient.present_mutations))
            #     + 'and {} mutations were unique to single samples.'.format(len(patient.shared_muts[1])))

            self.file.write(self._inds[self._ind]+'</figcaption>\n')
            self.file.write(self._inds[self._ind]+'</div>\n')
            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</figure>\n')

            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</div>\n')
            self.file.write(self._inds[self._ind]+'</div>\n')

        self.file.write(self._inds[self._ind]+'</br>\n\n')

    def add_similarity_information(self, patient):
        """
        Add tables providing the Jaccard similarity coefficient and the genetic distance between all pairs of
        samples to the HTML report.
        :param patient: instance of class patient
        """

        self.file.write(self._inds[self._ind]+'<h4>Genetic similarity</h4>\n')

        # add table with the Jaccard similarity coefficient between all pairs of samples
        self.file.write(self._inds[self._ind] + '<table class="table table-striped" '
                        + 'style="text-align: center;width:98%;max-width:800px;font-size:9pt">\n')
        self._ind += 1      # indentation level increases by 1

        # add table caption
        self.file.write(self._inds[self._ind]
                        + '<caption>Jaccard similarity coefficient between all pairs of samples.</caption>\n')

        col_names = ['Sample'] + patient.sample_names
        header = ''.join('<th class="text-center">{}</th>'.format(col_name.replace('_', ' ')) for col_name in col_names)
        self.file.write(self._inds[self._ind]+header+'\n')

        # build up output data sequentially
        for sa1_idx, sample_name in enumerate(patient.sample_names):

            row = list()
            row.append(sample_name.replace('_', ' '))

            for sa2_idx in range(len(patient.sample_names)):
                row.append('{:.2f}'.format(patient.sim_coff[sa1_idx][sa2_idx]))

            # write row to file
            self.file.write(self._inds[self._ind]+'<tr>'+''.join('<td>{}</td>'.format(c) for c in row)+'</tr>\n')

        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</table>\n\n')

        # self.file.write(self._inds[self._ind]+'</br>\n\n')

        # add table with the genetic distance between all pairs of samples
        self.file.write(self._inds[self._ind] + '<table class="table table-striped" '
                        + 'style="text-align: center;width:98%;max-width:800px;font-size:9pt">\n')
        self._ind += 1      # indentation level increases by 1

        # add table caption
        self.file.write(self._inds[self._ind]
                        + '<caption>Genetic distance between all pairs of samples.</caption>\n')

        col_names = ['Sample'] + patient.sample_names
        header = ''.join('<th class="text-center">{}</th>'.format(col_name.replace('_', ' ')) for col_name in col_names)
        self.file.write(self._inds[self._ind]+header+'\n')

        # build up output data sequentially
        for sa1_idx, sample_name in enumerate(patient.sample_names):

            row = list()
            row.append(sample_name.replace('_', ' '))

            for sa2_idx in range(len(patient.sample_names)):
                row.append('{}'.format(patient.gen_dis[sa1_idx][sa2_idx]))

            # write row to file
            self.file.write(self._inds[self._ind]+'<tr>'+''.join('<td>{}</td>'.format(c) for c in row)+'</tr>\n')

        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</table>\n')

        self.file.write(self._inds[self._ind]+'</br>\n\n')

        # write temporary results to file
        self.file.flush()
        os.fsync(self.file.fileno())

    def add_conflict_graph(self, patient, mp_graph_name, phylogeny=None):
        """
        Add evolutionary conflict plot graph to the HTML report
        :param patient: instance of class patient
        :param mp_graph_name: path to the evolutionary conflict graph plot file
        :param phylogeny:
        """

        self.file.write(self._inds[self._ind]+'<h4>Evolutionary conflict graph</h4>\n')

        self.file.write(self._inds[self._ind]+'<div align="center">\n')
        self.file.write(self._inds[self._ind]+'<div style="width:98%;max-width:700px">\n')
        self._ind += 1      # indentation level increases by 1

        self.file.write(self._inds[self._ind]+'<figure>\n')
        self._ind += 1      # indentation level increases by 1
        self.file.write(self._inds[self._ind]+'<img class="img-responsive" src="'+mp_graph_name +
                                              '" alt="Evolutionary conflict graph" width="500"/>'+'\n')
        self.file.write(self._inds[self._ind]+'<div align="left">\n')
        self.file.write(self._inds[self._ind]+'<figcaption>\n')
        self.file.write(
            self._inds[self._ind]+'<b>Evolutionary conflict graph of {} samples in patient {}.</b>\n'.format(
                len(patient.sample_names), patient.name))
        self.file.write(
            self._inds[self._ind] + 'Treeomics considered {:.0f} distinct mutation patterns (MPs).\n'.format(
                math.pow(2, len(patient.sample_names))+1))
        self.file.write(self._inds[self._ind]+'Each circular line represents a distinct sample. '
                        + 'Inner to outer lines denote: '
                        + ', '.join(sa_name.replace('_', ' ') for sa_name in patient.sample_names)
                        + '. Marks on these lines denote present variants. \n')
        self.file.write(
            self._inds[self._ind]+'Labels denote the MP reliability scores. ' +
            'Only nodes with the highest reliability score are depicted. ' +
            'Blue colored nodes (MPs) are evolutionarily compatible ' +
            'and red colored nodes are evolutionarily incompatible indicated by edges among the nodes.' +
            '{}.\n'.format(' Minimum reliability score value to be considered as a potential subclone: {:.3f}'.format(
                phylogeny.min_score)) if phylogeny is not None else '')

        self.file.write(self._inds[self._ind]+'</figcaption>\n')
        self.file.write(self._inds[self._ind]+'</div>\n')
        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</figure>\n')

        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</div>\n')
        self.file.write(self._inds[self._ind]+'</div>\n')

        self.file.write(self._inds[self._ind]+'</br>\n\n')

    def add_inc_mp_information(self, phylogeny, incomp_mps_plot_filepath=None, plot_width=None):
        """
        Add table with sequencing data information about the incompatible mutation patterns and add illustrative plot
        about the VAF and coverage in these incompatible patterns if a path is given.
        :param phylogeny: data structure around the inferred phylogenetic tree
        :param incomp_mps_plot_filepath: path to illustrative sequencing data plot of incompatible mutation patterns
        :param plot_width: width of the plot
        """

        self.file.write(self._inds[self._ind]+'<h4>Evolutionarily incompatible mutation patterns</h4>\n')

        pat = phylogeny.patient

        # add table with the genetic distance between all pairs of samples
        self.file.write(self._inds[self._ind] + '<table class="table table-striped" '
                        + 'style="text-align: center;width:98%;max-width:800px;font-size:9pt">\n')
        self._ind += 1      # indentation level increases by 1

        col_names = ['Variant'] + pat.sample_names
        header = ''.join('<th class="text-center">{}</th>'.format(col_name.replace('_', ' ')) for col_name in col_names)
        self.file.write(self._inds[self._ind]+header+'\n')

        # build up output data sequentially
        if pat.gene_names is not None:
            for mut_idx in sorted(phylogeny.conflicting_mutations, key=lambda k: pat.gene_names[k].lower()):

                self.file.write(
                    self._inds[self._ind] + '<tr><td><em>{}</em> ({})</td> {} </tr>\n'.format(
                        pat.gene_names[mut_idx], pat.mut_keys[mut_idx],
                        ' '.join('<td> {}/{} </td>'.format(
                            pat.mut_reads[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]],
                            pat.coverage[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]]) for sa_idx, sa_name in
                            enumerate(sorted(pat.sample_names)))))
        else:
            for mut_idx in sorted(phylogeny.conflicting_mutations, key=lambda k: pat.mut_keys[k].lower()):
                self.file.write(
                    self._inds[self._ind] + '<tr><td>{}</td> {} </tr>\n'.format(
                        pat.mut_keys[mut_idx], ' '.join('<td> {}/{} </td>'.format(
                            pat.mut_reads[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]],
                            pat.coverage[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]]) for sa_idx, sa_name in
                            enumerate(sorted(pat.sample_names)))))

        self._ind -= 1      # indentation level decreases by 1
        self.file.write(self._inds[self._ind]+'</table>\n')

        # show illustrative plot of the sequencing data of the incompatible mutation patterns
        if incomp_mps_plot_filepath is not None:
            self.file.write(self._inds[self._ind]+'<div align="center">\n')
            self.file.write(self._inds[self._ind]+'<div style="width:98%;max-width:700px">\n')
            self._ind += 1      # indentation level increases by 1

            self.file.write(self._inds[self._ind]+'<figure>\n')
            self._ind += 1      # indentation level increases by 1
            self.file.write(self._inds[self._ind]+'<img class="img-responsive" src="'+incomp_mps_plot_filepath +
                            '" alt="Sequencing data plot of incompatible mutation patterns" width="{}"/>'.format(
                                plot_width)+'\n')
            self.file.write(self._inds[self._ind]+'<div align="left">\n')
            self.file.write(self._inds[self._ind]+'<figcaption>\n')
            self.file.write(self._inds[self._ind]
                            + '<b>Incompatible mutation patterns in patient {}.</b>\n'.format(pat.name))

            present_mutations = pat.present_mutations
            self.file.write(self._inds[self._ind]
                            + 'Treeomics identified {} incompatible mutation patterns '.format(
                len(phylogeny.conflicting_mutations)) + '(out of {} investigated variants; {:.1%}).'.format(
                len(present_mutations), float(len(phylogeny.conflicting_mutations)) / len(present_mutations))+'\n')

            self.file.write(self._inds[self._ind]
                            + ' The color of the border of each rectangle representing a variant illustrates the '
                              'original classification, '
                            + 'the color of the left bar within each rectangle illustrates the VAF, '
                            + 'and the color of the right bar illustrates the coverage.  \n')
            self.file.write(self._inds[self._ind]
                            + 'Blue borders correspond to variants classified as present, red absent variants, '
                              'and light red unknown mutation status.\n')

            self.file.write(self._inds[self._ind]+'</figcaption>\n')
            self.file.write(self._inds[self._ind]+'</div>\n')
            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</figure>\n')

            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</div>\n')
            self.file.write(self._inds[self._ind]+'</div>\n')

    def add_artifacts_information(self, phylogeny, artifacts_plot_filepath=None, plot_width=None):
        """
        Add table with sequencing data information of the putative artifacts and add illustrative plot
        about the VAF and coverage in these artifacts if a path is given.
        :param phylogeny: data structure around the inferred phylogenetic tree
        :param artifacts_plot_filepath: illustrative sequencing data plot for the putative artifacts
        :param plot_width: width of the plot
        """

        self.file.write(self._inds[self._ind]+'<h4>Data artifacts</h4>\n')

        pat = phylogeny.patient

        # add information about putative sequencing errors
        no_fps = sum(len(fps) for mut_idx, fps in phylogeny.false_positives.items())
        no_fns = sum(len(fns) for mut_idx, fns in phylogeny.false_negatives.items())
        no_putative_artifacts = no_fps+no_fns

        # any evolutionarily incompatible variants due to limited search space
        if phylogeny.conflicting_mutations is not None and len(phylogeny.conflicting_mutations) > 0:
            self.file.write(self._inds[self._ind]+'<h5>Unclassified artifacts due to limited solution space:</h5>\n')
            self.file.write(self._inds[self._ind]+'<ul>\n')
            self._ind += 1      # indentation level increases by 1

            for mut_idx in sorted(phylogeny.conflicting_mutations,
                                  key=lambda x: pat.gene_names[x].lower() if pat.gene_names is not None
                                  else pat.mut_keys[x]):
                self.file.write(
                    self._inds[self._ind] + '<li><em>{}</em> {} in samples: {} </li>\n'.format(
                        pat.gene_names[mut_idx] if pat.gene_names is not None else pat.mut_keys[mut_idx],
                        '({})'.format(pat.mut_keys[mut_idx]) if pat.gene_names is not None else '',
                        ', '.join('{} (reads: {}/{})'.format(
                            pat.sample_names[sa_idx].replace('_', ' '),
                            pat.mut_reads[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]],
                            pat.coverage[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]]) for sa_idx in
                            sorted(range(len(pat.sample_names)), key=lambda x: pat.sample_names[x]))))
                            # if math.exp(pat.log_p01[mut_idx][sa_idx][1]) > 0.5)))

            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</ul></br>\n')

        # any putative false-positives (sequencing errors)?
        if len(phylogeny.false_positives.keys()) > 0:
            self.file.write(self._inds[self._ind]+'<h5>Putative false-positives:</h5>\n')
            self.file.write(self._inds[self._ind]+'<ul>\n')
            self._ind += 1      # indentation level increases by 1

            for mut_idx, samples in sorted(phylogeny.false_positives.items(),
                                           key=lambda x: pat.gene_names[x[0]].lower() if pat.gene_names is not None
                                           else pat.mut_keys[x[0]]):
                self.file.write(
                    self._inds[self._ind] + '<li><em>{}</em> {} in samples: {} </li>\n'.format(
                        pat.gene_names[mut_idx] if pat.gene_names is not None else pat.mut_keys[mut_idx],
                        '({})'.format(pat.mut_keys[mut_idx]) if pat.gene_names is not None else '',
                        ', '.join('{} (reads: {}/{})'.format(
                            pat.sample_names[sa_idx].replace('_', ' '),
                            pat.mut_reads[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]],
                            pat.coverage[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]]) for sa_idx in
                            sorted(samples, key=lambda x: pat.sample_names[x])
                            if sa_idx in pat.mutations[mut_idx])))

            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</ul></br>\n')

        # any information about putative lost variants?
        if len(phylogeny.false_negatives.keys()) > 0:
            self.file.write(self._inds[self._ind]+'<h5>Putative lost variants:</h5>\n')
            self.file.write(self._inds[self._ind]+'<ul>\n')
            self._ind += 1      # indentation level increases by 1

            for mut_idx, samples in sorted(phylogeny.false_negatives.items(),
                                           key=lambda x: pat.gene_names[x[0]].lower() if pat.gene_names is not None
                                           else pat.mut_keys[x[0]]):
                self.file.write(
                    self._inds[self._ind]+'<li><em>{}</em> {} in samples: {} </li>\n'.format(
                        pat.gene_names[mut_idx] if pat.gene_names is not None else pat.mut_keys[mut_idx],
                        '({})'.format(pat.mut_keys[mut_idx]) if pat.gene_names is not None else '',
                        ', '.join('{} (reads: {}/{})'.format(
                            pat.sample_names[sa_idx].replace('_', ' '),
                            pat.mut_reads[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]],
                            pat.coverage[pat.mut_keys[mut_idx]][pat.sample_names[sa_idx]]) for sa_idx
                            in sorted(samples, key=lambda x: pat.sample_names[x])
                            if sa_idx not in pat.mutations[mut_idx] and pat.data[mut_idx][sa_idx] >= 0)))

            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</ul>\n')

        if artifacts_plot_filepath is not None:
            present_mutations = pat.present_mutations
            if len(phylogeny.false_positives.keys()) + len(phylogeny.false_negatives.keys()) > 0:
                self.file.write(self._inds[self._ind]+'<div align="center">\n')
                self.file.write(self._inds[self._ind]+'<div style="width:98%;max-width:700px">\n')
                self._ind += 1      # indentation level increases by 1

                self.file.write(self._inds[self._ind]+'<figure>\n')
                self._ind += 1      # indentation level increases by 1
                self.file.write(self._inds[self._ind]+'<img class="img-responsive" src="'+artifacts_plot_filepath +
                                '" alt="Mutation patterns of putative artifacts" width="{}"/>'.format(plot_width)+'\n')
                self.file.write(self._inds[self._ind]+'<div align="left">\n')
                self.file.write(self._inds[self._ind]+'<figcaption>\n')
                self.file.write(self._inds[self._ind]
                                + '<b>Mutation patterns of putative artifacts in patient {}.</b>\n'.format(pat.name))

                self.file.write(self._inds[self._ind]
                                + 'Treeomics identified {} putative artifacts '.format(no_putative_artifacts)
                                + '(out of {} investigated variants; {:.1%}).'.format(
                                len(pat.sample_names) * len(present_mutations),
                                float(no_putative_artifacts) / (len(pat.sample_names) * len(present_mutations)))+'\n')
                self.file.write(
                    self._inds[self._ind] +
                    'Additionally there were {} putative false-negatives due to insufficient '.format(
                        sum(len(fns) for mut_idx, fns in phylogeny.false_negative_unknowns.items()))
                    + 'coverage (unknowns; data not shown). \n')

                self.file.write(self._inds[self._ind]
                                + ' The color of the border of each rectangle representing a variant illustrates the '
                                  'original classification, '
                                + 'the color of the left bar within each rectangle illustrates the VAF, '
                                + 'and the color of the right bar illustrates the coverage. '
                                + 'If a variant was identified as a putative artifact, a smaller rectangle '
                                  'with the changed classification color is added on top of the bars. \n')
                self.file.write(self._inds[self._ind]
                                + 'Blue borders correspond to variants classified as present, red absent variants, '
                                  'and light red unknown mutation status.\n')

                self.file.write(self._inds[self._ind]+'</figcaption>\n')
                self.file.write(self._inds[self._ind]+'</div>\n')
                self._ind -= 1      # indentation level decreases by 1
                self.file.write(self._inds[self._ind]+'</figure>\n')

                self._ind -= 1      # indentation level decreases by 1
                self.file.write(self._inds[self._ind]+'</div>\n')
                self.file.write(self._inds[self._ind]+'</div>\n')

            else:       # there are no putative well-powered artifacts
                self.file.write(self._inds[self._ind]+'<p>\n')
                self._ind += 1      # indentation level increases by 1
                self.file.write(self._inds[self._ind] + 'Treeomics identified no well-powered artifacts '
                                + '(out of {} investigated variants; {:.1%}).'.format(
                                len(pat.sample_names) * len(present_mutations),
                                float(no_putative_artifacts) / (len(pat.sample_names) * len(present_mutations)))+'\n')
                self.file.write(
                    self._inds[self._ind] +
                    'There were {} putative false-negatives due to insufficient '.format(
                        sum(len(fns) for mut_idx, fns in phylogeny.false_negative_unknowns.items()))
                    + 'coverage (unknowns; data not shown). \n')

                self._ind -= 1      # indentation level decreases by 1
                self.file.write(self._inds[self._ind]+'</p>\n')

    def end_report(self, e, c0, max_absent_vaf, loh_frequency, fpr, fdr,
                   min_absent_cov, min_median_cov, min_median_maf):
        """
        Add used parameter values, HTML file footer, and close the file
        :param e: sequencing error rate for bayesian inference
        :param c0: prior mixture parameter of delta function and uniform distribution for bayesian inference
        :param max_absent_vaf: maximal absent VAF before considering estimated purity
        :param loh_frequency: probability that a SNV along a lineage is lost due loss of heterozygosity
        :param fpr: false-positive rate
        :param fdr: false-discovery rate
        :param min_absent_cov: Minimum coverage for a variant to be called absent
        :param min_median_cov: minimum median coverage of a sample to pass filtering
        :param min_median_maf: minimum median variant allele frequency of a sample to pass filtering
        """

        if self.file is not None:

            self.file.write(self._inds[self._ind]+'</br><p><em>Treeomics settings:</em>\n')
            self.file.write(
                self._inds[self._ind] + ' sequencing error rate e: {}, '.format(e)
                + 'prior absent probability c0: {}, '.format(c0)
                + 'max absent VAF: {}, '.format(max_absent_vaf)
                + 'LOH frequency: {}, '.format(loh_frequency)
                + 'false discovery rate: {}, '.format(fdr)
                + 'false-positive rate: {}. '.format(fpr)
                + ('Absent classification minimum coverage: {}. '.format(min_absent_cov) if min_absent_cov > 0 else '')
                + ('Sample minimal median coverage: {}. '.format(min_median_cov) if min_median_cov > 0 else '')
                + ('Sample minimal median VAF minimum {}. '.format(min_median_maf) if min_median_maf > 0 else '')
                + ('Filter: minimum VAF per variant in at least one sample {}. '.format(settings.MIN_VAF)
                    if (settings.MIN_VAF is not None and settings.MIN_VAF > 0) else '')
                + ('Filter: minimum number of variant reads per variant in at least one sample {}. '.format(
                    settings.MIN_VAR_READS) if settings.MIN_VAR_READS is not None and settings.MIN_VAR_READS > 0
                   else ''))

            self.file.write(self._inds[self._ind]+'</p>\n')

            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</div> <!-- /container -->\n')

            # add footer
            today = datetime.date.today()
            self.file.write(self._inds[self._ind]+'<footer class="footer">\n')
            self._ind += 1      # indentation level increases by 1
            self.file.write(self._inds[self._ind]+'<div class="container">\n')
            self._ind += 1      # indentation level increases by 1
            self.file.write(self._inds[self._ind]+'<p class="text-muted">&copy; Treeomics {}.{}.{}, '.format(
                VERSION[0], VERSION[1], VERSION[2]) + today.strftime('%b %d, %Y')+'</p>\n')
            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</div>\n')
            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</footer>\n')

            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</body>\n')
            self._ind -= 1      # indentation level decreases by 1
            self.file.write(self._inds[self._ind]+'</html>\n')

            self.file.flush()
            self.file.close()

            self.file = None
