#encoding:utf-8
#!/usr/bin/python
main_table_design="""main_table(
    transcript_id int unsigned NOT NULL auto_increment,
    transcript_name text NOT NULL,
    gene_name text NOT NULL,
    transcript_seq mediumtext NOT NULL,
    cds_select int default 0,
    aa_homology int default 0,
    primary key(transcript_id)
    )"""
orf_find_table_design="""orf_find(
    annotation_id int unsigned NOT NULL auto_increment,
    transcript_id int NOT NULL,
    cds_start int NOT NULL,
    cds_end int NOT NULL,
    longest_cds_start int NOT NULL,
    longest_cds_end int NOT NULL,
    primer_style tinytext NOT NULL,
    strand char(1) NOT NULL,
    primary key(annotation_id)
    )"""
usearch_alignment_table_design="""usearch(
    align_id int unsigned NOT NULL auto_increment,
    annotation_id int NOT NULL,
    transcript_id int NOT NULL,
    protein_name text NOT NULL,
    indent float NOT NULL,
    coverage float NOT NULL,
    taget_coverage float NOT NULL,
    primary key(align_id)
    )"""
