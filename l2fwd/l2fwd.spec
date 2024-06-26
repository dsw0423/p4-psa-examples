
struct ethernet_t {
	bit<48> dst_addr
	bit<48> src_addr
	bit<16> ether_type
}

struct psa_ingress_output_metadata_t {
	bit<8> class_of_service
	bit<8> clone
	bit<16> clone_session_id
	bit<8> drop
	bit<8> resubmit
	bit<32> multicast_group
	bit<32> egress_port
}

struct psa_egress_output_metadata_t {
	bit<8> clone
	bit<16> clone_session_id
	bit<8> drop
}

struct psa_egress_deparser_input_metadata_t {
	bit<32> egress_port
}

struct l2fwd_arg_t {
	bit<32> port_out
}

header ethernet instanceof ethernet_t

struct local_metadata_t {
	bit<32> psa_ingress_input_metadata_ingress_port
	bit<8> psa_ingress_output_metadata_drop
	bit<32> psa_ingress_output_metadata_multicast_group
	bit<32> psa_ingress_output_metadata_egress_port
}
metadata instanceof local_metadata_t

action l2fwd args instanceof l2fwd_arg_t {
	mov m.psa_ingress_output_metadata_drop 0
	mov m.psa_ingress_output_metadata_multicast_group 0x0
	mov m.psa_ingress_output_metadata_egress_port t.port_out
	return
}

action drop_1 args none {
	mov m.psa_ingress_output_metadata_drop 1
	return
}

table l2fwd_table {
	key {
		h.ethernet.dst_addr exact
	}
	actions {
		l2fwd
		drop_1
	}
	default_action drop_1 args none 
	size 0x400
}


apply {
	rx m.psa_ingress_input_metadata_ingress_port
	mov m.psa_ingress_output_metadata_drop 0x1
	extract h.ethernet
	table l2fwd_table
	jmpneq LABEL_DROP m.psa_ingress_output_metadata_drop 0x0
	emit h.ethernet
	tx m.psa_ingress_output_metadata_egress_port
	LABEL_DROP :	drop
}


